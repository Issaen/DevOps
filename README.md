# PT_Docker
БД ставились на Ubuntu 22.04
Проверьте, что пользователям выданы права в sudoers

#Также проверьте файл inventory.
Запускайте python bot.py 
Запуск через ansible-playbook playbook_tg_bot.yml --ask-become-pass
Введите имя обычного юзера машинки на которой запущена БД-мастер, чтобы бот выводил логи
После того как playbook отраюотал, в папке с ботом нужно создать .env

