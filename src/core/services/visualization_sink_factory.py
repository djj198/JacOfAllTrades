import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Type
from pydantic import create_model, BaseModel, ValidationError

from src.interfaces.protocols import QuantLLMProtocol
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.financial_insight import InsightNode, InsightEdge, QuantSummary
from src.core.primitives.data_ref import DataRef
from src.core.services.safe_lambda_readers import SafeLambdaReaderRegistry

logger = logging.getLogger(__name__)

class VisualizationSinkFactoryError(Exception):
    """Exception raised for errors in the VisualizationSinkFactory."""
    pass

class VisualizationSinkFactory:
    """
    Factory for creating VisualizationSink objects using dynamic Pydantic models.
    Supports Phase 2 Schema-Heavy Hybrid strategy.
    """

    @staticmethod
    def create(prompt: str, llm_provider: QuantLLMProtocol) -> VisualizationSink:
        """
        Main entry point for creating a VisualizationSink.
        """
        try:
            # TODO (Jac): BEGIN - Schema generation / LLM call
            # This logic will be replaced by a Jac walker calling `by llm()` for schema generation.
            schema = llm_provider.generate_schema(prompt)
            # TODO (Jac): END - Schema generation / LLM call

            # TODO (Jac): BEGIN - Pydantic model creation
            # Building a validated model from the LLM-provided JSON Schema.
            # In Phase 2, we use Pydantic v2 create_model.
            DynamicModel = VisualizationSinkFactory._create_dynamic_model(schema)
            # TODO (Jac): END - Pydantic model creation

            # TODO (Jac): BEGIN - Graph construction / primitive embedding
            # Reasoning and data generation matching the dynamic schema.
            raw_data = llm_provider.generate_insight_data(prompt, schema)
            
            # Validate data against the dynamic model
            try:
                validated_data = DynamicModel(**raw_data)
            except ValidationError as e:
                raise VisualizationSinkFactoryError(f"Data validation failed: {e}") from e

            # Construct the internal graph structure (nodes, edges)
            # This logic currently maps the validated model back to our core primitives.
            nodes = []
            # We assume the validated_data has a standard structure or we map it
            # For MVP, we expect 'nodes', 'edges', 'summary' fields if they exist in schema
            
            raw_nodes = getattr(validated_data, 'nodes', [])
            for node_data in raw_nodes:
                node_dict = node_data if isinstance(node_data, dict) else node_data.model_dump()
                
                # TODO (Jac): BEGIN - Reader attachment
                # Check for DataRef and attach readers from registry
                if "path" in node_dict.get("data", {}) and "reader_name" in node_dict.get("data", {}):
                    data_ref_dict = node_dict["data"]
                    data_ref = DataRef.from_dict(data_ref_dict)
                    reader = SafeLambdaReaderRegistry.get_reader(data_ref.reader_name)
                    if reader:
                        # Attachment in Phase 2 means wrapping or adding the reader result to data
                        # In this pure sync version, we might just verify it exists
                        # or embed the reader's "lazy" result.
                        node_dict["data"] = reader(data_ref.path, data_ref.params)
                    else:
                        logger.warning(f"No reader found for {data_ref.reader_name}")
                # TODO (Jac): END - Reader attachment
                
                nodes.append(InsightNode.from_dict(node_dict))

            edges = [InsightEdge.from_dict(e if isinstance(e, dict) else e.model_dump()) 
                    for e in getattr(validated_data, 'edges', [])]
            
            summary_data = getattr(validated_data, 'summary', "Summary generated via LLM.")
            quant_summary = QuantSummary.from_dict(summary_data)

            sink = VisualizationSink(
                insight_id=str(uuid.uuid4()),
                prompt=prompt,
                created_at=datetime.now(timezone.utc).isoformat(),
                quant_summary=quant_summary,
                nodes=tuple(nodes),
                edges=tuple(edges),
                root_node_id=getattr(validated_data, 'root_node_id', None),
                visualizer_pseudo_prompt=prompt,
                suggested_chart_types=getattr(validated_data, 'suggested_chart_types', ["bar"])
            )
            # TODO (Jac): END - Graph construction / primitive embedding

            return sink

        except VisualizationSinkFactoryError:
            # Already logged or explicitly handled
            raise
        except NotImplementedError as e:
            # Expected when using stubs or partially implemented providers
            raise VisualizationSinkFactoryError(str(e)) from e
        except Exception as e:
            logger.exception(f"Unexpected error in VisualizationSinkFactory: {e}")
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
