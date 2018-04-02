# tpcc-util

## Описание

tpcc - утилита для упрощения работы с курсом tpcc-course-2018 в МФТИ.

## Установка

Для корректной установки утилиты необходим python версии 3.5 или выше с рабочим `pip3`.

Обращаю внимание, что будет использован `/usr/bin/python3`, так как другие
версии (например, поставляемые с anaconda), ведут себя не так, как ожидается.

Для установки необходимо выполнить
```bash
$ ./install.sh
```

В процессе установки будут загружены необходимые для работы пакеты, а также создана ссылка
`/usr/bin/tpcc`.

Также в процессе установки будет создана папка `~/.tpcc`, в который будет находится конфигурационный
файл, а также логи и другие файлы, необходимые для работы приложения.
 
В случае проблем с установкой пишите, будем разбираться.

## Конфигурация

При установке будет создан файл `~/.tpcc/config.json` следующего содержания:
```json
{
        "gitlab_token": "<gitlab_token>",
        "path_to_repos": "<path_to_repos>",
        "course_repo_name": "tpcc-course-2018",
        "group_number": "<group_number>",
        "first_name": "<first_name>",
        "last_name": "<last_name>",
        "assignee_username": "<assignee_username>",
        "gitlab_repo_user": "tpcc-course-2018",
        "test_before_merge": true
}
```

Для работы программы необходимо заполнить все имеющиеся поля. Получение токена для работы с
API GitLab подробно описан [здесь](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

`path_to_repos` --- путь к директории, в которой лежат репозиторий курса и репозиторий `solutions`.

`assignee_username` следует писать без знака @ --- `tau0`, но не `@tau0`

## Использование

### Переключаемся на задачу

Всё взаимодействие с утилитой производится в формате `tpcc OPTION`. Важная особенность утилиты:
директория, из которой производится запуск, **не имеет значения**, то есть для сборки и тестирования
не потребуется менять рабочую директорию на `build` текущей задачи, всё произойдёт автоматически.


Первая опция, необходимая для успешной работы: `task`. Единственное этой команды - смена 
текущей задачи. Например, чтобы переключиться на задачу `1-mutex/futex`, нужно вызвать
```bash
$ tpcc task 1-mutex/futex
```

Она создаст файл решения если его не существовало, подгрузит шаблон решения, если его название соответствует названию задачи, 
в данном случае - `futex.hpp`. Но к сожалению файл с шаблоном называется `solution_ref.hpp`, поэтому вы должны увидеть
что-то такое:

```text
Solution template futex.hpp not found. Specify solution template file:
        tpcc task --template <template_file> 1-mutex/futex
or specify --no-template option to create empty file:
        tpcc task --no-template 1-mutex/futex
``` 

Как мы видим, программа не нашла файл. Следуя совету программы, запустим
```bash
$ tpcc task --template solution_ref.hpp 1-mutex/futex
```

Также существует сокращённая версия:
```bash
$ tpcc task -t solution_ref.hpp 1-mutex/futex
```

Теперь, после того, как мы создали решение, хочется открыть его для редактирования. Для этого
хочется использовать команду `tpcc ide <ide_name>`, но она будет добавлена лишь в будущих версиях :)

### Сборка и тестирование

Для создания `Makefile` нужно написать
```bash
$ tpcc build
```
, что эквивалентно запуску `cmake ..`в директории `build` со всеми необходимыми параметрами.
Если на вашей системе не будет обнаружен clang++ версии 5.0 или старше, 
то запуск `tpcc build` завершится с ошибкой.

Для тестирования используется опция `test`:

```bash
$ tpcc test
```
по умолчанию запускающая все тесты. Вывод должен полностью соответствовать выводу `make run_...`. 
Также можно добавить опцию с указанием группы тестов:
```bash
$ tpcc test TEST_TYPE
``` 
Возможные опции: `asan`, `tsan`, `unit`, `stress` и `all` (по умолчанию).

Для того, чтобы отформатировать код, достаточно вызвать
```bash
$ tpcc style
```
Чтобы этот вызов сработал необходим `clang-format`.

### Отправка решения

Для отправки решения в репозиторий есть опция `commit`, которая позволит вам отправить 
решение на GitLab. Чтобы это сделать, достаточно переключиться на нужную задачу и написать

```bash
$ tpcc commit
```

В этот момент возникает вопрос: "А на той ли я вообще задаче?"
```bash
$ tpcc status
```
выведет имя текущей задачи, то есть
```text
1-mutex/futex
```

Итак, мы на нужной задаче, поэтому всё-таки вызовем
```bash
$ tpcc commit
```

Это создаст коммит с некоторым разумным комментарием и отправит его на GitLab. Если же вам
очень хочется написать своё сообщение, вы можете это сделать так же, как и в git'е:

```bash
$ tpcc commit -m "Я сделяль"
```

### Создание merge-request'а

Для создания merge-request'а на GitLab достаточно вызвать
```bash
$ tpcc merge
```
Это приведёт к созданию merge-request'а с правильным названием, проставленными тегами и проверяющим,
которого вы указали в конфигурационном файле. Также этот вызов по умолчанию запустит все тесты,
чтобы удостовериться в корректности решения. Если этого хочется избежать, нужно добавить
специальный флаг `--no-tests`:

```bash
$ tpcc merge --no-tests
```

Если же вы хотите отключить тестирование перманентно, достаточно изменить в конфугурационном
файле ключ 
```json
"test_before_merge": false
```
