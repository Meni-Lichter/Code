"""Performance Testing Metrics and Utilities"""

import time
import functools
import pytest
from typing import Callable, Any
import statistics


class PerformanceMetrics:
    """Track performance metrics across tests"""
    
    def __init__(self):
        self.timings = {}
        self.memory_usage = {}
        
    def record_timing(self, test_name: str, duration: float):
        """Record test execution time"""
        if test_name not in self.timings:
            self.timings[test_name] = []
        self.timings[test_name].append(duration)
    
    def get_stats(self, test_name: str) -> dict:
        """Get statistics for a test"""
        if test_name not in self.timings or not self.timings[test_name]:
            return {}
        
        timings = self.timings[test_name]
        return {
            'count': len(timings),
            'total': sum(timings),
            'mean': statistics.mean(timings),
            'median': statistics.median(timings),
            'min': min(timings),
            'max': max(timings),
            'stdev': statistics.stdev(timings) if len(timings) > 1 else 0
        }
    
    def print_summary(self):
        """Print performance summary"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUMMARY")
        print("="*80)
        
        for test_name in sorted(self.timings.keys()):
            stats = self.get_stats(test_name)
            if stats:
                print(f"\n{test_name}:")
                print(f"  Executions: {stats['count']}")
                print(f"  Mean Time:  {stats['mean']*1000:.2f} ms")
                print(f"  Median:     {stats['median']*1000:.2f} ms")
                print(f"  Min:        {stats['min']*1000:.2f} ms")
                print(f"  Max:        {stats['max']*1000:.2f} ms")
                if stats['stdev'] > 0:
                    print(f"  Std Dev:    {stats['stdev']*1000:.2f} ms")
        
        print("\n" + "="*80)
        print(f"Total tests tracked: {len(self.timings)}")
        print("="*80 + "\n")


# Global metrics instance
_metrics = PerformanceMetrics()


def time_test(func: Callable) -> Callable:
    """Decorator to time test execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            test_name = func.__name__
            _metrics.record_timing(test_name, duration)
            
            # Print individual test timing
            print(f"\n⏱️  {test_name}: {duration*1000:.2f} ms")
    
    return wrapper


def measure_operation(operation_name: str):
    """Context manager to measure specific operations"""
    class OperationTimer:
        def __init__(self, name):
            self.name = name
            self.start_time = None
            self.duration = None
        
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self
        
        def __exit__(self, *args):
            end_time = time.perf_counter()
            self.duration = end_time - self.start_time
            _metrics.record_timing(self.name, self.duration)
            print(f"    ⏱️  {self.name}: {self.duration*1000:.2f} ms")
    
    return OperationTimer(operation_name)


@pytest.fixture(scope="session", autouse=True)
def performance_summary(request):
    """Print performance summary at end of test session"""
    yield
    _metrics.print_summary()


def get_metrics() -> PerformanceMetrics:
    """Get global metrics instance"""
    return _metrics
