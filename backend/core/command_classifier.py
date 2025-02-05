from transformers import pipeline
import logging
from typing import Tuple, Dict, List
from utils.exceptions import ClassificationError

logger = logging.getLogger(__name__)

class CommandClassifier:
    def __init__(self):
        try:
            # Load model and tokenizer
            model_name = "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                device="cpu"  # Force CPU usage
            )
            logger.info("Classifier initialized on CPU")

            # Command types and categories
            self.command_types = [
                "create new task",
                "delete existing task",
                "update task",
                "mark task complete",
                "create reminder",
                "show tasks",
                "system control"
            ]

            self.task_categories = [
                "Work",
                "Personal",
                "Shopping",
                "Errands",
                "Health",
                "Bills/Finance",
                "Learning",
                "Other"
            ]

        except Exception as e:
            logger.error(f"Failed to initialize classifier: {str(e)}")
            raise ClassificationError(f"Classifier initialization failed: {str(e)}")

    def classify_command(self, text: str) -> Dict[str, any]:
        """
        Classify the type of command and extract task category if applicable
        """
        try:
            logger.info(f"Received text for classification: '{text}' (type: {type(text)})")

            # First, determine the command type
            command_hypothesis = "This is a command to {}"
            command_result = self.classifier(
                text,
                self.command_types,
                hypothesis_template=command_hypothesis,
                multi_label=False
            )

            command_type = command_result['labels'][0]
            command_confidence = command_result['scores'][0]

            result = {
                'command_type': command_type,
                'confidence': command_confidence
            }

            # If it's a task-related command, classify the category
            if "task" in command_type and "show" not in command_type:
                category_hypothesis = "This task belongs to category {}"
                category_result = self.classifier(
                    text,
                    self.task_categories,
                    hypothesis_template=category_hypothesis,
                    multi_label=False
                )

                result['category'] = category_result['labels'][0]
                result['category_confidence'] = category_result['scores'][0]

            logger.debug(f"Classification result for '{text}': {result}")
            return result

        except Exception as e:
            logger.error(f"Classification failed for text '{text}': {str(e)}")
            raise ClassificationError(f"Failed to classify command: {str(e)}")

    def cleanup(self):
        """Explicit cleanup method"""
        logger.info("Classifier cleanup completed")

    def __del__(self):
        try:
            self.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")