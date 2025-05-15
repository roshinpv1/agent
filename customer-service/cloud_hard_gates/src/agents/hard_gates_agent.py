from typing import Dict, List, Any
from google.adk.agents import Agent
from src.models.model_config import ModelConfig
from src.prompts.hard_gates_prompts import GLOBAL_INSTRUCTION
from src.tools.validation_tools import validation_tools

class HardGatesAgent(Agent):
    def __init__(
        self,
        model_config: ModelConfig,
        description: str = "A validation agent that performs cloud hard gates validation."
    ):
        super().__init__(
            model=model_config.get_client(),
            description=description,
            tools=validation_tools,
            global_instruction=GLOBAL_INSTRUCTION
        )

    async def validate_criteria(self, criteria_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a specific criteria.
        
        Args:
            criteria_id: The ID of the criteria to validate
            context: Additional context for validation
            
        Returns:
            Dict containing the validation results
        """
        try:
            # Find the appropriate validation tool
            validation_tool = next(
                tool for tool in self.tools 
                if tool.name == f"validate_{criteria_id}"
            )
            
            # Perform the validation
            result = await validation_tool(context)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def validate_chain(self, criteria_ids: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate a chain of criteria in sequence.
        
        Args:
            criteria_ids: List of criteria IDs to validate
            context: Additional context for validation
            
        Returns:
            List of validation results
        """
        results = []
        for criteria_id in criteria_ids:
            result = await self.validate_criteria(criteria_id, context)
            results.append(result)
        return results

    async def generate_validation_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a markdown validation report from the results.
        
        Args:
            results: List of validation results
            
        Returns:
            Markdown formatted validation report
        """
        report = ["# Cloud Hard Gates Validation Report\n"]
        
        # Group results by category
        infrastructure_results = [r for r in results if r.get("criteria_id") in ["alerting", "monitoring", "recoverability"]]
        application_results = [r for r in results if r.get("criteria_id") in ["auditability", "availability", "error_handling", "testing"]]
        
        # Infrastructure section
        report.append("## Infrastructure/Platform Validation\n")
        for result in infrastructure_results:
            report.append(f"### {result['criteria_id']}\n")
            report.append(f"Status: {result['status']}\n")
            report.append("#### Checks:\n")
            for check in result['checks']:
                report.append(f"- {check['name']}: {check['status']}")
                if check['recommendations']:
                    report.append("  - Recommendations:")
                    for rec in check['recommendations']:
                        report.append(f"    - {rec}")
            report.append("\n")
        
        # Application section
        report.append("## Application Validation\n")
        for result in application_results:
            report.append(f"### {result['criteria_id']}\n")
            report.append(f"Status: {result['status']}\n")
            report.append("#### Checks:\n")
            for check in result['checks']:
                report.append(f"- {check['name']}: {check['status']}")
                if check['recommendations']:
                    report.append("  - Recommendations:")
                    for rec in check['recommendations']:
                        report.append(f"    - {rec}")
            report.append("\n")
        
        return "\n".join(report) 