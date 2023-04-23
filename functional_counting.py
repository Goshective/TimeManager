from datetime import datetime


class Date_picker:
    def time_string(time_s):
        items = [
            (31536000, '{} г. '),
            (2592000, '{} мес. '),
            (604800, '{} нед. '),
            (86400, '{} д. '),
            (3600, '{} ч.'),
        ]
        
        if time_s == 0:
            return None

        if time_s < 3600:
            if time_s <= 60: return 'меньше минуты'
            return f'{time_s//60} мин.'

        result = ''
        c = 0
        for value, fmt in items:
            if time_s >= value:
                if c == 2:
                    break
                result += fmt.format(int(time_s / value))
                time_s %= value
                c += 1

        return result
    
    def get_time(t0, t1):
        time_s = int((t1 - t0).total_seconds())
        if time_s == 0: return 'Только что'
        return f'{Date_picker.time_string(abs(time_s))} {"назад" if time_s > 0 else "вперёд"}'.capitalize()


d2 = datetime(2022, 1, 15, 16, 17, 39)
d1 = datetime(2020, 12, 14, 10, 1, 0)
# print(Date_picker.get_time(d1, d2))