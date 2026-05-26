from app.engine.types import CheckResult


class ScoreAggregator:
    def aggregate(self, results: list[CheckResult]) -> float:
        active = [result for result in results if result.weight > 0]
        if not active:
            return 100.0
        total_weight = sum(result.weight for result in active)
        weighted_score = sum(result.score * result.weight for result in active)
        return round((weighted_score / total_weight) * 100, 1)

