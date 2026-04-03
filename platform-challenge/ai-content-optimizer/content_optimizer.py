#!/usr/bin/env python3
"""
AI Content Optimizer
Optimizes content for AI model training and inference
"""

import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    """Content types."""
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    DOCUMENTATION = "documentation"

@dataclass
class OptimizationResult:
    """Content optimization result."""
    original_score: float
    optimized_score: float
    improvements: List[str]
    optimized_content: str

class ContentQualityAnalyzer:
    """Analyzes and scores content quality for AI training."""

    def analyze_quality(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyze content quality."""
        
        metrics = {
            "readability_score": self._calculate_readability(content),
            "completeness_score": self._calculate_completeness(content),
            "consistency_score": self._calculate_consistency(content),
            "clarity_score": self._calculate_clarity(content),
            "structure_score": self._calculate_structure(content)
        }
        
        overall_score = sum(metrics.values()) / len(metrics)
        
        return {
            "content_type": content_type,
            "overall_quality_score": round(overall_score, 2),
            "metrics": {k: round(v, 2) for k, v in metrics.items()},
            "issues": self._identify_quality_issues(metrics),
            "recommendations": self._generate_quality_recommendations(metrics)
        }

    def tokenize_for_ai(self, content: str) -> Dict[str, Any]:
        """Tokenize content for AI model training."""
        
        # Estimate token count (rough approximation)
        words = content.split()
        estimated_tokens = len(words) * 1.3  # Average ~1.3 tokens per word
        
        return {
            "word_count": len(words),
            "estimated_tokens": int(estimated_tokens),
            "sentence_count": len([s for s in content.split('.') if s.strip()]),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "vocabulary_size": len(set(w.lower() for w in words)),
            "token_efficiency": round(len(set(w.lower() for w in words)) / len(words), 3)
        }

    def extract_training_pairs(self, content: str) -> List[Dict[str, str]]:
        """Extract question-answer pairs for training."""
        
        pairs = []
        paragraphs = content.split('\n\n')
        
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 50:
                # Extract key sentences
                sentences = [s.strip() for s in para.split('.') if s.strip()]
                
                if len(sentences) > 1:
                    # Create Q&A pairs from sentences
                    for j in range(len(sentences) - 1):
                        pairs.append({
                            "question": f"What about {sentences[j][:50]}?",
                            "answer": sentences[j+1],
                            "source": f"paragraph_{i}"
                        })
        
        return pairs

    # ===== Private Methods =====

    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (0-10)."""
        
        if not content:
            return 0
        
        words = content.split()
        sentences = [s for s in content.split('.') if s.strip()]
        
        if not sentences or not words:
            return 0
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # Flesch-Kincaid like scoring
        readability = 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / len(words))
        readability = min(10, max(0, readability / 20))  # Normalize to 0-10
        
        return float(readability)

    def _calculate_completeness(self, content: str) -> float:
        """Calculate completeness score (0-10)."""
        
        if not content:
            return 0
        
        # Check for structure
        has_intro = len(content) > 100
        has_examples = 'example' in content.lower() or 'e.g.' in content
        has_conclusion = content.count('.') > 3
        
        completeness = 0
        if has_intro:
            completeness += 3
        if has_examples:
            completeness += 4
        if has_conclusion:
            completeness += 3
        
        return float(completeness)

    def _calculate_consistency(self, content: str) -> float:
        """Calculate consistency score (0-10)."""
        
        if not content:
            return 0
        
        # Check for consistent formatting
        lines = content.split('\n')
        consistency = 7  # Base score
        
        # Penalize for inconsistent capitalization
        caps_lines = sum(1 for line in lines if line and line[0].isupper())
        if caps_lines > 0:
            consistency += 1
        
        # Penalize for inconsistent punctuation
        consistency = min(10, consistency)
        
        return float(consistency)

    def _calculate_clarity(self, content: str) -> float:
        """Calculate clarity score (0-10)."""
        
        if not content:
            return 0
        
        words = content.split()
        clarity = 5
        
        # Longer content is harder to understand
        if len(words) > 1000:
            clarity -= (len(words) - 1000) / 200
        
        # Check for clear language
        jargon_count = sum(1 for w in words if len(w) > 15)
        clarity -= jargon_count / len(words) * 5
        
        return float(max(0, min(10, clarity)))

    def _calculate_structure(self, content: str) -> float:
        """Calculate structure score (0-10)."""
        
        if not content:
            return 0
        
        structure = 0
        
        # Check for headings
        if '#' in content or '=' in content:
            structure += 2
        
        # Check for lists
        if '- ' in content or '* ' in content or '1. ' in content:
            structure += 2
        
        # Check for paragraphs
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        if paragraphs > 2:
            structure += 3
        
        # Check for code blocks or examples
        if '```' in content or '>' in content:
            structure += 3
        
        return float(min(10, structure))

    def _identify_quality_issues(self, metrics: Dict[str, float]) -> List[str]:
        """Identify quality issues."""
        
        issues = []
        
        for metric, score in metrics.items():
            if score < 5:
                issues.append(f"Low {metric}: {score}/10")
        
        return issues

    def _generate_quality_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations."""
        
        recommendations = []
        
        if metrics.get('readability_score', 0) < 5:
            recommendations.append("Simplify language and shorten sentences")
        
        if metrics.get('completeness_score', 0) < 5:
            recommendations.append("Add more examples and details")
        
        if metrics.get('structure_score', 0) < 5:
            recommendations.append("Add headings, lists, and paragraphs for better structure")
        
        if metrics.get('clarity_score', 0) < 5:
            recommendations.append("Reduce jargon and explain technical terms")
        
        return recommendations


class DatasetOptimizer:
    """Optimizes datasets for AI training."""

    def optimize_dataset(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize dataset for training."""
        
        if not dataset:
            return {"error": "Empty dataset"}
        
        # Calculate statistics
        stats = self._calculate_dataset_stats(dataset)
        
        # Check for quality issues
        issues = self._identify_dataset_issues(dataset)
        
        # Generate optimizations
        optimizations = self._generate_optimizations(dataset, issues)
        
        return {
            "original_size": len(dataset),
            "statistics": stats,
            "issues": issues,
            "optimizations": optimizations,
            "estimated_improvement": self._estimate_improvement(issues)
        }

    def balance_classes(self, dataset: List[Dict], class_field: str) -> Dict[str, Any]:
        """Balance class distribution in dataset."""
        
        from collections import Counter
        
        if not dataset or class_field not in dataset[0]:
            return {"error": "Invalid dataset or class field"}
        
        # Count classes
        class_counts = Counter(item[class_field] for item in dataset)
        
        max_count = max(class_counts.values())
        balanced = []
        
        for item in dataset:
            balanced.append(item)
            # Duplicate underrepresented samples
            class_label = item[class_field]
            if class_counts[class_label] < max_count:
                class_counts[class_label] += 1
                balanced.append(item.copy())
        
        return {
            "original_size": len(dataset),
            "balanced_size": len(balanced),
            "class_distribution": dict(Counter(item[class_field] for item in balanced)),
            "samples_added": len(balanced) - len(dataset)
        }

    def remove_duplicates(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Remove duplicate entries."""
        
        if not dataset:
            return {"error": "Empty dataset"}
        
        seen = set()
        unique = []
        duplicates_removed = 0
        
        for item in dataset:
            key = json.dumps(item, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                unique.append(item)
            else:
                duplicates_removed += 1
        
        return {
            "original_size": len(dataset),
            "unique_size": len(unique),
            "duplicates_removed": duplicates_removed,
            "deduplication_rate": round(duplicates_removed / len(dataset), 3) if dataset else 0
        }

    def filter_quality_data(self, dataset: List[Dict], min_quality_score: float = 0.7) -> Dict[str, Any]:
        """Filter dataset to keep only high-quality entries."""
        
        analyzer = ContentQualityAnalyzer()
        filtered = []
        
        for item in dataset:
            if 'content' in item or 'text' in item:
                content = item.get('content') or item.get('text')
                quality = analyzer.analyze_quality(content)
                
                if quality['overall_quality_score'] >= min_quality_score:
                    filtered.append(item)
        
        return {
            "original_size": len(dataset),
            "filtered_size": len(filtered),
            "removed": len(dataset) - len(filtered),
            "retention_rate": round(len(filtered) / len(dataset), 3) if dataset else 0
        }

    # ===== Private Methods =====

    def _calculate_dataset_stats(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Calculate dataset statistics."""
        
        return {
            "total_samples": len(dataset),
            "average_fields": len(dataset[0]) if dataset else 0,
            "field_names": list(dataset[0].keys()) if dataset else []
        }

    def _identify_dataset_issues(self, dataset: List[Dict]) -> List[str]:
        """Identify dataset issues."""
        
        issues = []
        
        # Check for missing values
        missing_count = 0
        for item in dataset:
            for value in item.values():
                if value is None or value == "":
                    missing_count += 1
        
        if missing_count > 0:
            issues.append(f"{missing_count} missing values found")
        
        # Check for duplicates
        seen = set()
        duplicates = 0
        for item in dataset:
            key = json.dumps(item, sort_keys=True, default=str)
            if key in seen:
                duplicates += 1
            seen.add(key)
        
        if duplicates > 0:
            issues.append(f"{duplicates} duplicate entries found")
        
        return issues

    def _generate_optimizations(self, dataset: List[Dict], issues: List[str]) -> List[str]:
        """Generate optimization suggestions."""
        
        optimizations = []
        
        if any('missing' in issue for issue in issues):
            optimizations.append("Implement missing value imputation")
        
        if any('duplicate' in issue for issue in issues):
            optimizations.append("Remove duplicate entries")
        
        if len(dataset) < 100:
            optimizations.append("Dataset is small - consider data augmentation")
        
        return optimizations

    def _estimate_improvement(self, issues: List[str]) -> float:
        """Estimate improvement percentage."""
        
        improvement = 0
        if issues:
            improvement = min(30, len(issues) * 10)
        
        return float(improvement)


class ModelOptimizer:
    """Optimizes AI model configuration."""

    def analyze_model_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze model configuration for optimization."""
        
        recommendations = []
        issues = []
        
        # Check learning rate
        lr = config.get('learning_rate', 0.001)
        if lr > 0.1:
            issues.append(f"Learning rate {lr} may be too high")
            recommendations.append("Consider reducing learning rate to 0.001-0.01")
        
        # Check batch size
        batch_size = config.get('batch_size', 32)
        if batch_size > 256:
            issues.append(f"Batch size {batch_size} may cause memory issues")
            recommendations.append("Try smaller batch sizes (32-128)")
        
        # Check epochs
        epochs = config.get('epochs', 10)
        if epochs < 3:
            issues.append("Too few epochs may underfit model")
            recommendations.append("Train for at least 5-10 epochs")
        
        # Check for missing configs
        required_fields = ['model_type', 'layers', 'activation', 'optimizer']
        missing = [f for f in required_fields if f not in config]
        if missing:
            issues.append(f"Missing configuration: {', '.join(missing)}")
        
        return {
            "config_summary": {k: v for k, v in config.items() if k in ['model_type', 'learning_rate', 'batch_size', 'epochs']},
            "issues": issues,
            "recommendations": recommendations,
            "optimization_score": round(max(0, 10 - len(issues) * 2), 1)
        }

    def suggest_hyperparameters(self, dataset_size: int, model_type: str = "neural_network") -> Dict[str, Any]:
        """Suggest hyperparameters based on dataset size."""
        
        # Learning rate suggestion
        if dataset_size < 1000:
            lr = 0.01
        elif dataset_size < 10000:
            lr = 0.001
        else:
            lr = 0.0001
        
        # Batch size suggestion
        if dataset_size < 100:
            batch_size = 16
        elif dataset_size < 10000:
            batch_size = 32
        else:
            batch_size = 64
        
        # Epochs suggestion
        if dataset_size < 100:
            epochs = 100
        elif dataset_size < 1000:
            epochs = 50
        else:
            epochs = 10
        
        return {
            "dataset_size": dataset_size,
            "model_type": model_type,
            "suggested_hyperparameters": {
                "learning_rate": lr,
                "batch_size": batch_size,
                "epochs": epochs,
                "optimizer": "adam",
                "loss_function": "categorical_crossentropy",
                "validation_split": 0.2,
                "early_stopping_patience": 5
            },
            "reasoning": {
                "learning_rate": f"Adjusted for dataset size {dataset_size}",
                "batch_size": "Balanced for memory and convergence",
                "epochs": "Sufficient for convergence without overfitting"
            }
        }


class ContentOptimizer:
    """Main optimizer for all content types."""

    def __init__(self):
        self.quality_analyzer = ContentQualityAnalyzer()
        self.dataset_optimizer = DatasetOptimizer()
        self.model_optimizer = ModelOptimizer()

    def optimize_all(self, content: str, dataset: List[Dict] = None, model_config: Dict = None) -> Dict[str, Any]:
        """Optimize content, dataset, and model config."""
        
        results = {}
        
        # Optimize content
        results['content_optimization'] = self.quality_analyzer.analyze_quality(content)
        
        # Optimize dataset if provided
        if dataset:
            results['dataset_optimization'] = self.dataset_optimizer.optimize_dataset(dataset)
        
        # Optimize model config if provided
        if model_config:
            results['model_optimization'] = self.model_optimizer.analyze_model_config(model_config)
        
        # Overall recommendation
        results['overall_recommendation'] = self._generate_overall_recommendation(results)
        
        return results

    def _generate_overall_recommendation(self, results: Dict) -> str:
        """Generate overall recommendation."""
        
        issues = []
        
        if 'content_optimization' in results:
            if results['content_optimization']['overall_quality_score'] < 6:
                issues.append("Improve content quality")
        
        if 'dataset_optimization' in results:
            if results['dataset_optimization'].get('issues'):
                issues.append("Clean and balance dataset")
        
        if 'model_optimization' in results:
            if results['model_optimization'].get('issues'):
                issues.append("Adjust model configuration")
        
        if not issues:
            return "All systems optimized - ready for training"
        else:
            return f"Priority: {', '.join(issues)}"


if __name__ == "__main__":
    optimizer = ContentOptimizer()
    
    content = """
    This is sample content for optimization.
    It contains multiple paragraphs and sentences.
    
    Example: This shows structure.
    
    Conclusion: All optimized.
    """
    
    dataset = [
        {"text": "Sample text 1", "label": "A"},
        {"text": "Sample text 2", "label": "B"},
    ]
    
    config = {
        "model_type": "neural_network",
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10
    }
    
    result = optimizer.optimize_all(content, dataset, config)
    
    import json
    print(json.dumps(result, indent=2, default=str))
