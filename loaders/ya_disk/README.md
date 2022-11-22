## ya_disk
Scripts for upload files to your Yandex Disk

### How to get token ([official guide](https://yandex.ru/dev/direct/doc/start/token.html))
1. Open [OAuthYandex](https://oauth.yandex.ru/)  
2. Add new application  
3. Descripte your application:  
    - Название сервиса  
    - Для какой платформы нужно приложение? (Веб-сервисы -> Подставить URL для разработки)  
    - Какие данные вам нужны? (Яндекс.Диск REST API)  
4. Click "Создать приложение"  
5. Click "Выгрузить готовый запросы"  
6. Find "Запрос на oauth code"
7. Copy link from `https://oauth.y..` to first square brackets. Delete all space from link. You must take somethink like this:  
`https://oauth.yandex.ru/authorize?response_type=code&client_id=<your_id>&redirect_uri=<your_uri>%2Fverification_code`  
8. Past link in to your browser  
9. Sign in if needed  
10. Copy **Code**  
11. Copy **ClientID** and **ClientSecret** from application page  
12. Run `python3 get_token.py -c ClientID -s ClientSecret -o Code`
