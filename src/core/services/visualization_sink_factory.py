import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Type
from pydantic import create_model, BaseModel, ValidationError

from src.interfaces.protocols import QuantLLMProtocol
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.financial_insight import InsightNode, InsightEdge, QuantSummary

logger = logging.getLogger(__name__)

class VisualizationSinkFactoryError(Exception):
    """Exception raised for errors in the VisualizationSinkFactory."""
    pass

class VisualizationSinkFactory:
    """
    Factory for creating VisualizationSink objects using dynamic Pydantic models.
    Simplified for rich brute-force portfolio-aware refactor.
    """

    @staticmethod
    def create(prompt: str, llm_provider: QuantLLMProtocol) -> VisualizationSink:
        """
        Main entry point for creating a VisualizationSink.
        """
        try:
            # 1. Schema generation
            schema = llm_provider.generate_schema(prompt)

            # 2. Pydantic model creation (dynamic validation)
            DynamicModel = VisualizationSinkFactory._create_dynamic_model(schema)

            # 3. Data generation matching the dynamic schema
            raw_data = llm_provider.generate_insight_data(prompt, schema)
            
            # 4. Validate data against the dynamic model
            try:
                validated_data = DynamicModel(**raw_data)
            except ValidationError as e:
                raise VisualizationSinkFactoryError(f"Data validation failed: {e}") from e

            # 5. Construct the internal graph structure (nodes, edges)
            # Brute-force mapping: directly use validated data fields
            nodes = [InsightNode.from_dict(n) for n in getattr(validated_data, 'nodes', [])]
            edges = [InsightEdge.from_dict(e) for e in getattr(validated_data, 'edges', [])]
            
            summary_data = getattr(validated_data, 'quant_summary', {"title": "Summary", "summary_text": "No summary provided"})
            quant_summary = QuantSummary.from_dict(summary_data)

            sink = VisualizationSink(
                insight_id=getattr(validated_data, 'insight_id', str(uuid.uuid4())),
                prompt=prompt,
                created_at=datetime.now(timezone.utc).isoformat(),
                quant_summary=quant_summary,
                nodes=tuple(nodes),
                edges=tuple(edges),
                root_node_id=getattr(validated_data, 'root_node_id', None),
                visualizer_pseudo_prompt=getattr(validated_data, 'visualizer_pseudo_prompt', prompt),
                suggested_chart_types=getattr(validated_data, 'suggested_chart_types', ["bar"]),
                rendered_payload=getattr(validated_data, 'rendered_payload', {})
            )

            return sink

        except Exception as e:
            logger.exception(f"Error in VisualizationSinkFactory: {e}")
            raise VisualizationSinkFactoryError(str(e)) from e

    @staticmethod
    def _create_dynamic_model(schema: Dict[str, Any]) -> Type[BaseModel]:
        """
        Creates a Pydantic model from a JSON Schema.
        """
        # Minimal implementation for JSON Schema -> Pydantic
        # In a full implementation, we'd use a library like datamodel-code-generator
        # or recursively build the model. For MVP, we handle simple field types.
        
        fields = {}
        properties = schema.get("properties", {})
        for field_name, field_info in properties.items():
            field_type = field_info.get("type")
            # Map JSON Schema types to Python types
            python_type: Any = Any
            if field_type == "string":
                python_type = str
            elif field_type == "number":
                python_type = float
            elif field_type == "integer":
                python_type = int
            elif field_type == "boolean":
                python_type = bool
            elif field_type == "array":
                python_type = List[Any]
            elif field_type == "object":
                python_type = Dict[str, Any]
            
            # Default value
            default = ... if field_name in schema.get("required", []) else None
            fields[field_name] = (python_type, default)

        return create_model("DynamicInsightModel", **fields)
