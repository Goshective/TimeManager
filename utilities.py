from datetime import datetime
import random
import string


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
        if time_s == 0:
            return 'Сегодня'
        elif time_s > 0:
            return f'{Date_picker.time_string(abs(time_s))} назад'.capitalize()
        return f'Через {Date_picker.time_string(abs(time_s))}'
    

def date_max():
    return datetime.now()

def date_min():
    return datetime(datetime.now().year - 1, 1, 1)

def full_list(lst):
    ret = [lst[0]]
    for i in range(1, len(lst)):
        if lst[i - 1] < lst[i] - 1:
            ret.append('...')
        ret.append(lst[i])
    return ret

def get_pages(n, c):
    if n < 7:
        return list(range(2, n))
    elif c <= 4 or n - 3 <= c:
        start = [] if c == 1 else [2] if c == 2 else [2, 3] if c == 3 else [2, c - 1]
        mid = [c] if 3 < c < n - 2 else []
        end = [] if c == n else [c] if c == n - 1 else [c, n - 1] if c == n - 2 else [c + 1, n - 1]
        return full_list(start + mid + end)
    else:
        return [2, '...', c-1, c, c+1, '...', n-1]

def get_page_after_delete(recs, cur_p, recs_p):
    if (recs - 1) % recs_p > 1: return cur_p
    return max(1, cur_p - 1)

def db_datetime_formating(t):
    normal_t = t.split(".")[0]
    return datetime.strptime(normal_t, '%Y-%m-%d %H:%M:%S')

def get_work_time(work_h, work_m):
    work_time = ""
    if work_h != 0: work_time += f" {work_h} ч."
    if work_m != 0: work_time += f" {work_m} мин."
    return work_time

def get_remaining_time_title(lst):
    ans = []
    for dct in lst:
        dt = dct['created_date']
        remain = Date_picker.get_time(dt, datetime.now())
        act_name = dct['name']
        work_time = f'{act_name} - затрачено' + get_work_time(dct['work_hours'], dct['work_min'])
        ans.append((dct['id'], remain, work_time))
    return ans

def get_token(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


"""d2 = datetime(2022, 1, 15, 16, 17, 39)
d1 = datetime(2020, 12, 14, 10, 1, 0)
print(Date_picker.get_time(d1, d2))"""