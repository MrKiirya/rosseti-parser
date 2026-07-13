# rosseti-parser

Парсер показаний двухтарифного электросчётчика с [личного кабинета Россети Московский регион](https://lk.rossetimr.ru) для интеграции с **Home Assistant**.

Сервис забирает последние показания **Т1 (день)** и **Т2 (ночь)** и отдаёт их в JSON. Дальше данные можно публиковать в **MQTT** → Home Assistant (`sensor.rosseti_t1`, `sensor.rosseti_t2`) → Recorder → аналитика.

```
Россети → rosseti-parser → MQTT → Home Assistant
```

## Возможности

- Авторизация на сайте Россетей
- Получение истории показаний
- Парсинг последнего значения Т1/Т2
- Публикация в MQTT → Home Assistant
- Расписание через APScheduler (daemon-режим)
- One-shot запуск для ручной проверки

## Быстрый старт (Docker)

```bash
cp .env.example .env
# заполните .env

# daemon с расписанием (по умолчанию)
docker compose up -d --build
docker compose logs -f

# разовый запуск → JSON
docker compose run --rm -e MODE=once rosseti-parser
```

> Для one-shot используйте `compose run` с `-e MODE=once`, не `up -d`.

## Локальный запуск (без Docker)

```bash
pip install -r requirements.txt
cp .env.example .env

python -m rosseti_parser              # one-shot
python -m rosseti_parser --daemon     # scheduler
python -m rosseti_parser --env-file .env
```

## Переменные окружения

| Переменная | Обязательная | Описание |
|------------|:------------:|----------|
| `LOGIN` | да | Email для входа в lk.rossetimr.ru |
| `PASSWORD` | да | Пароль |
| `METER_UUID` | да | UUID счётчика (из URL истории показаний) |
| `SCHEDULE` | нет | Время запуска, формат `HH:MM,HH:MM`. По умолчанию: `08:30,23:30` |
| `TZ` | нет | Часовой пояс для расписания. По умолчанию: `Europe/Moscow` |
| `MODE` | нет | `daemon` по умолчанию в Docker, `once` — разовый запуск |
| `DOCKER_RESTART` | нет | `unless-stopped` по умолчанию в Docker |
| `MQTT_HOST` | нет* | IP/hostname Mosquitto. Если задан — publish после каждого запуска |
| `MQTT_PORT` | нет | Порт MQTT. По умолчанию: `1883` |
| `MQTT_TOPIC` | нет | Topic. По умолчанию: `rosseti/meter` |
| `MQTT_USER` | нет | Логин MQTT |
| `MQTT_PASSWORD` | нет | Пароль MQTT |
| `MQTT_RETAIN` | нет | `true`/`false`. По умолчанию: `true` |

\* MQTT опционален: без `MQTT_HOST` — только JSON в stdout (one-shot) / логи (daemon).

Пример `.env`:

```env
LOGIN=your-email@example.com
PASSWORD=your-password
METER_UUID=00000000-0000-0000-0000-000000000000
SCHEDULE=08:30,23:30
TZ=Europe/Moscow

MQTT_HOST=192.168.1.100
MQTT_PORT=1883
MQTT_TOPIC=rosseti/meter
MQTT_USER=homeassistant
MQTT_PASSWORD=your-mqtt-password
MQTT_RETAIN=true
```

## Формат вывода

Двухтарифный счётчик:

```json
{
  "t1": 501,
  "t2": 187,
  "reading_date": "2026-07-05",
  "transmitted_by": "«Россети Московский регион»",
  "received_at": "2026-07-07T08:30:00+03:00",
  "source": "rosseti"
}
```

Однотарифный — значение в `t1`, `t2` = `null`.

## Home Assistant

MQTT sensors (`configuration.yaml`):

```yaml
mqtt:
  sensor:
    - name: "Россети Т1"
      unique_id: rosseti_t1
      state_topic: "rosseti/meter"
      value_template: "{{ value_json.t1 }}"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
      json_attributes_template: >
        {
          "reading_date": "{{ value_json.reading_date }}",
          "received_at": "{{ value_json.received_at }}",
          "transmitted_by": "{{ value_json.transmitted_by }}"
        }

    - name: "Россети Т2"
      unique_id: rosseti_t2
      state_topic: "rosseti/meter"
      value_template: "{{ value_json.t2 }}"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
      json_attributes_template: >
        {
          "reading_date": "{{ value_json.reading_date }}",
          "received_at": "{{ value_json.received_at }}",
          "transmitted_by": "{{ value_json.transmitted_by }}"
        }
```

## Деплой на Proxmox

1. Создать LXC Debian, включить **nesting**
2. Установить Docker
3. Скопировать проект в `/opt/rosseti-parser`
4. Создать `.env`
5. `docker compose up -d --build`

## Структура проекта

```
rosseti_parser/
├── api/        # HTTP-клиент, авторизация
├── parsing/    # парсинг HTML → MeterReading
├── output/     # payload + mqtt
├── runner.py   # одна итерация
└── scheduler.py
```

## Тесты

```bash
python -m unittest discover -s tests
```

## Roadmap

- [x] MQTT publish → Home Assistant
- [ ] AppDaemon Energy Engine
