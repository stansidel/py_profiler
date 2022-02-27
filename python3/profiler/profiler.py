from dataclasses import dataclass
from datetime import datetime, timedelta
from multiprocessing import Event
from typing import Optional
import statistics
import uuid


class Profiler:
    """Profiles events based on their start and end marks.
    
    Example usage:
    ```
    profiler = Profiler()

    run_uid = profiler.start('run_loop')
    for i in range(10):
        loop_uid = profiler.start('loop')
        time.sleep(int(random() * 3))
        profiler.stop(loop_uid)
        print(f'Iteration #{i + 1}')
    profiler.stop(run_uid)

    detailed_events_info = profiler.finished_events
    events_stats = profiler.finished_events_stats
    print(events_stats)
    ```

    Events with same names are tracked separately but grouped together to calculate stats on multiple
    runs of alike events.
    """

    @dataclass
    class Event:
        """An event tracked with `Profiler`.
        
        When the event hasn't finished, it has its `end_time` and `duration` set to `None`."""

        name: str
        start_time: datetime
        end_time: Optional[datetime] = None
        duration: Optional[int] = None


    __running_events: 'dict[uuid.UUID, Profiler.Event]'
    __finished_events: 'dict[str, list[Profiler.Event]]'

    def __init__(self):
        self.__running_events = {}
        self.__finished_events = {}

    def start(self, event: str) -> uuid.UUID:
        """Starts tracking a new event with name `name`.
        
        Used `stop(uid=uid)` with the returned value of `start` for `uid`
        to track the completion of the event."""
        id = uuid.uuid4()
        event = Profiler.Event(name=event, start_time=datetime.now())
        self.__running_events[id] = event
        return id
    
    def stop(self, uid: uuid.UUID) -> Optional[Event]:
        """Tracks completion of the event with the `uid` specified.
        
        You get the `uid` of the event as the return value from the `start` function."""
        if uid not in self.__running_events.keys():
            return None
        event = self.__running_events.pop(uid)
        end_time = datetime.now()
        event.end_time = end_time
        duration = end_time - event.start_time
        event.duration = duration.microseconds
        self.__save_finished_event(event)
        return event
    
    @property
    def finished_events(self) -> 'dict[str, list[Profiler.Event]]':
        """Full list of tracked events grouped by the event name."""
        return self.__finished_events
    
    @property
    def finished_events_stats(self) -> 'dict[str, dict[str, float]]':
        """Statistics for the tracked events.
        
        Keys of the returned dictionary contain names of the events finished so far.
        
        Values are dictionaries with stats.
        
        For groups with single value, the stats dictionary only contains single value — `value`.
        
        For groups with multiple values, the stats dictionary contains basic statistics for the values."""
        
        result: 'dict[str, dict[str, float]]' = {}
        for name, events in self.__finished_events.items():
            durations = map(lambda e: e.duration, events)
            result[name] = self.__get_stats_from_array(list(durations))
        return result
    
    def __save_finished_event(self, event: Event):
        name = event.name
        if name not in self.__finished_events:
            self.__finished_events[name] = []
        self.__finished_events[name].append(event)

    def __get_stats_from_array(self, values: 'list[int]') -> 'dict[str, float]':
        if len(values) == 0:
            return {}

        if len(values) == 1:
            return {'value': float(values[0])}

        return {
            'len': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values),
            'variance': statistics.variance(values)
        }
