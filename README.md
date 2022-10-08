# Социальная сеть Yatube
Это **сервис для публикации личных записей**, разработанный в рамках учебного 
курса от **Яндекс.Практикум**. 

## Описание
В проекте реализованы следующие функции:

- Добавление постов авторизованными пользователями
- Добавление группы и картинки к посту
- Редактирование/удаление поста разрешено только автору
- Авторизованные пользователи могут оставлять комментарии к постам
- Подписка/отписка на понравившихся авторов
- Создание отдельной ленты постов по группам(тематикам)
- Группы может создавать только администратор сайта.
- Отдельная ленты с постами от любимых авторов, на которых подписан пользователь

## Функционал:
- Регистрация/авторизация пользователя
- Смена пароля через почту
- В проект добавлены кастомные страницы ошибок:
  1. 404 page_not_found 
  2. 500 server_error
  3. 403 permission_denied_view
- Пагинация страниц
- Кеширование постов
- Анонимному пользователю доступно только чтение
- Покрытые тестами

## Настройка и запуск:
1. Клонируем репозиторий на локальную машину:
   ```bash
   git clone https://github.com/wurikavich/social_network_Yatube.git
   ```
2. Создаём и активируем виртуальное окружение:
   ```bash
   python -m venv venv
   
   source env/bin/activate
   ```
3. Устанавливаем зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создаём и применяем миграции:
   ```bash
   python manage.py makemigrations
   
   python manage.py migrate
   ```
5. Запускаем сервер:
   ```bash
   python manage.py runserver
   ```
Проект и админ-панель доступны по адресам:
   ```
  http://127.0.0.1:8000

  http://127.0.0.1:8000/admin
   ```
## Тестирование:
Выполнить команду:
   ```bash
   pytest
   ```
Результат должен быть такой:
```
tests/test_paginator.py::TestGroupPaginatorView::test_group_paginator_view_get PASSED                                                             [  3%]
tests/test_paginator.py::TestGroupPaginatorView::test_group_paginator_not_in_context_view PASSED                                                  [  6%]
tests/test_paginator.py::TestGroupPaginatorView::test_index_paginator_not_in_view_context PASSED                                                  [  9%]
tests/test_paginator.py::TestGroupPaginatorView::test_index_paginator_view PASSED                                                                 [ 12%]
tests/test_paginator.py::TestGroupPaginatorView::test_profile_paginator_view PASSED                                                               [ 15%]
tests/test_about.py::TestTemplateView::test_about_author_tech PASSED                                                                              [ 18%]
tests/test_auth_urls.py::TestAuthUrls::test_auth_urls PASSED                                                                                      [ 21%]
tests/test_comment.py::TestComment::test_comment_add_view PASSED                                                                                  [ 25%]
tests/test_comment.py::TestComment::test_comment_add_auth_view PASSED                                                                             [ 28%]
tests/test_create.py::TestCreateView::test_create_view_get PASSED                                                                                 [ 31%]
tests/test_create.py::TestCreateView::test_create_view_post PASSED                                                                                [ 34%]
tests/test_follow.py::TestFollow::test_follow_not_auth PASSED                                                                                     [ 37%]
tests/test_follow.py::TestFollow::test_follow_auth PASSED                                                                                         [ 40%]
tests/test_homework.py::TestPost::test_post_create PASSED                                                                                         [ 43%]
tests/test_homework.py::TestGroup::test_group_create PASSED                                                                                       [ 46%]
tests/test_homework.py::TestGroupView::test_group_view PASSED                                                                                     [ 50%]
tests/test_homework.py::TestCustomErrorPages::test_custom_404 PASSED                                                                              [ 53%]
tests/test_homework.py::TestCustomErrorPages::test_custom_500 PASSED                                                                              [ 56%]
tests/test_homework.py::TestCustomErrorPages::test_custom_403 PASSED                                                                              [ 59%]
tests/test_post.py::TestPostView::test_index_post_with_image PASSED                                                                               [ 62%]
tests/test_post.py::TestPostView::test_index_post_caching PASSED                                                                                  [ 65%]
tests/test_post.py::TestPostView::test_post_view_get PASSED                                                                                       [ 68%]
tests/test_post.py::TestPostEditView::test_post_edit_view_get PASSED                                                                              [ 71%]
tests/test_post.py::TestPostEditView::test_post_edit_view_author_get PASSED                                                                       [ 75%]
tests/test_post.py::TestPostEditView::test_post_edit_view_author_post PASSED                                                                      [ 78%]
tests/test_profile.py::TestProfileView::test_profile_view_get PASSED                                                                              [ 81%]
tests/test_comment.py::TestComment::test_comment_model PASSED                                                                                     [ 84%]
tests/test_follow.py::TestFollow::test_follow[author] PASSED                                                                                      [ 87%]
tests/test_follow.py::TestFollow::test_follow[user] PASSED                                                                                        [ 90%]
tests/test_homework.py::TestPost::test_post_model PASSED                                                                                          [ 93%]
tests/test_homework.py::TestPost::test_post_admin PASSED                                                                                          [ 96%]
tests/test_homework.py::TestGroup::test_group_model PASSED                                                                                        [100%]

===================================================================== 32 passed in 2.28s ===============================================================

```
## Стек технологий
- Python 3.10 
- Django 2.2.28,
- SQLite3
- Pillow 9.0.1 
- Pytest 6.2.5
- Unittest



## Разработчик
[Александр Гетманов](https://github.com/SelfGenius)
