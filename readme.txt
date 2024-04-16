Восстановление буквы "ё"

find . -name "*Петр" -exec rename 's/Петр/Пётр/' {} \;
find . -name "*Петр *" -exec rename -n 's/Петр /Пётр /' {} \;
find . -name "*Федор*" -exec rename 's/Федор/Фёдор/' {} \;
find . -name "*Семен*" -exec rename 's/Семен/Семён/' {} \;
rename 's/Алферов/Алфёров/' *
rename 's/Алешин/Алёшин/' *
rename 's/Алехин/Алёхин/' *
rename 's/Аксенов/Аксёнов/' *
rename 's/Киселев/Киселёв/' *
rename 's/Муравьев/Муравьёв/' *
rename 's/Москалев/Москалёв/' *
rename 's/Горбачев/Горбачёв/' *
rename 's/Грачев/Грачёв/' *
rename 's/Дремов/Дрёмов/' *
rename 's/Еремин/Ерёмин/' *
rename 's/Еременко/Ерёменко/' *
rename 's/Пушкарев/Пушкарёв/' *
rename 's/Рублев /Рублёв /' *


Удаление служебных символов
find . -name "*quot;*" -exec rename 's/quot;//g' {} \;
find . -name "*&amp;*" -print
find . -name "*&amp;*" -exec rename 's/&amp;//g' {} \;


Конвертирование win1251 в utf-8


Конвертирование fb2 в epub
fb2mobi.py --profile liberation --output-format epub Arhivarius_Voyna_mirov_Tom_2.fb2