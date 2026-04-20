"""
Benchmark script for embedding providers
"""

import time
import sys
import os
from typing import List, Dict
import statistics

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.skills.embedding_skill import EmbeddingSkill

class EmbeddingBenchmark:
    """Benchmark embedding providers"""
    
    def __init__(self):
        self.test_texts = [
            "Machine learning is transforming software development",
            "ClickHouse is a fast analytical database",
            "Python is widely used for data science",
            "Vector embeddings enable semantic search",
            "Large language models understand natural language"
        ]
    
    def benchmark_provider(self, provider: str, runs: int = 3) -> Dict:
        """
        Benchmark a specific provider
        
        Args:
            provider: Provider name
            runs: Number of test runs
            
        Returns:
            Benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking: {provider.upper()}")
        print(f"{'='*60}")
        
        try:
            skill = EmbeddingSkill(provider=provider)
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return {
                'provider': provider,
                'status': 'failed',
                'error': str(e)
            }
        
        latencies = []
        dimensions = None
        errors = 0
        
        for run in range(runs):
            print(f"\nRun {run + 1}/{runs}")
            run_latencies = []
            
            for i, text in enumerate(self.test_texts, 1):
                try:
                    start = time.time()
                    embedding = skill.generate(text)
                    latency = (time.time() - start) * 1000  # Convert to ms
                    
                    if embedding:
                        run_latencies.append(latency)
                        if dimensions is None:
                            dimensions = len(embedding)
                        print(f"  ✓ Text {i}: {latency:.0f}ms ({len(embedding)} dims)")
                    else:
                        errors += 1
                        print(f"  ✗ Text {i}: No embedding generated")
                        
                except Exception as e:
                    errors += 1
                    print(f"  ✗ Text {i}: {e}")
            
            if run_latencies:
                avg_latency = statistics.mean(run_latencies)
                latencies.extend(run_latencies)
                print(f"  Run avg: {avg_latency:.0f}ms")
        
        if not latencies:
            return {
                'provider': provider,
                'status': 'failed',
                'errors': errors
            }
        
        return {
            'provider': provider,
            'status': 'success',
            'dimensions': dimensions,
            'runs': runs,
            'texts_per_run': len(self.test_texts),
            'total_requests': len(latencies),
            'errors': errors,
            'latency': {
                'min': min(latencies),
                'max': max(latencies),
                'mean': statistics.mean(latencies),
                'median': statistics.median(latencies),
                'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            'throughput': 1000 / statistics.mean(latencies)  # requests per second
        }
    
    def run_all(self):
        """Run benchmarks for all providers"""
        providers = ['huggingface', 'perplexity', 'openai']
        results = []
        
        print("\n" + "="*60)
        print("EMBEDDING PROVIDER BENCHMARKS")
        print("="*60)
        
        for provider in providers:
            result = self.benchmark_provider(provider, runs=2)
            results.append(result)
            time.sleep(2)  # Cooldown between providers
        
        self.print_summary(results)
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print benchmark summary"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        successful = [r for r in results if r['status'] == 'success']
        
        if not successful:
            print("❌ No successful benchmarks")
            return
        
        # Print comparison table
        print(f"\n{'Provider':<15} {'Dims':<8} {'Avg (ms)':<12} {'Med (ms)':<12} {'RPS':<8}")
        print("-" * 60)
        
        for result in successful:
            provider = result['provider']
            dims = result['dimensions']
            avg = result['latency']['mean']
            med = result['latency']['median']
            rps = result['throughput']
            
            print(f"{provider:<15} {dims:<8} {avg:<12.0f} {med:<12.0f} {rps:<8.1f}")
        
        # Find best performer
        fastest = min(successful, key=lambda x: x['latency']['mean'])
        print(f"\n🏆 Fastest: {fastest['provider'].upper()} ({fastest['latency']['mean']:.0f}ms avg)")
        
        # Find most reliable
        most_reliable = min(successful, key=lambda x: x['errors'])
        if most_reliable['errors'] == 0:
            print(f"✅ Most Reliable: {most_reliable['provider'].upper()} (0 errors)")

if __name__ == '__main__':
    benchmark = EmbeddingBenchmark()
    results = benchmark.run_all()
