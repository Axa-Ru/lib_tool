#!/bin/bash

########################################################################
#
#   Набор скриптов для добавления в библиотеку TRAUM обновлений
#
#
VERSION="0.3"	# Axa. 2014/10/11


########################################################################

DEBUG=0

# Структура каталогов
#   ....\Traum                - корневая библиотека 
#        |
#        +--epub.vYYMM		  - библиотека на год YY месяц MM
#        |  |
#        |  +-en              - книги на английском
#        |  |  +--A
#        |  |  +--B
#        |  |  +--C
#        |  |
#        |  +--ru             - книги на русском
#        |     +--A
#        |     +--Б
#        |     +--В
#        |
#        +--fb2conv           - программа конвертвации fb2 -> epub
#        +--lib-update        - корневой рабочий каталог для update
#           |
#           +--fb2            - книги для update в формате fb2
#           +--epub           - результат конвертации в формате epub
#           |  +--en              в кодировке utf8
#           |  |  +--A
#           |  |  +--B
#           |  |  +--C
#           |  |
#           |  +--ru
#           |     +--A
#           |     +--Б
#           |     +--В
#           |
#           +--fb2-err        - книги, которые не сконвертировались

LIBV="0233"
if [ $DEBUG -eq 1 ]; then
	LIB_ROOT="/media/axa/Trans-1"
else
	LIB_ROOT="/home/axa/Media/nas4d0/Books/Traum"
fi
LIB_RU="${LIB_ROOT}/epub.v$LIBV/ru"
LIB_EN="${LIB_ROOT}/epub.v$LIBV/en"
UPD_FB2="${LIB_ROOT}/lib-update/fb2"
UPD_ERR="${LIB_ROOT}/lib-update/fb2-err"
UPD_EPUB_RU="${LIB_ROOT}/lib-update/epub/__ru__ok"
UPD_EPUB_EN="${LIB_ROOT}/lib-update/epub/__en__ok"
FB2CONV=/home/axa/Media/nas4d0/Books/Traum/fb2conv/fb2conv.py

#----------------------------------------------------------------------
#  Внутренние функции
#----------------------------------------------------------------------
# Удаляет пробелы, символы пунктуации, автора номер серии из названия книги
# и переводит все в lower case
aBNTrimWS()
{
#	((DEBUG)) && echo "[D:$FUNCNAME]"
	RET=$(echo "$1" | sed 's/[Ёё]/е/g; s/^[A-Za-яА-Яа-я]* [0-9]\{0,4\}//g; s/epub//; s/[”«»"“\.,=—?_…»–:-]//g; s/( /(/; s/[ ]\+/ /g; s/^ //g; s/./\L&/g')
	echo "$RET"
}

# Удаляет пробелы, символы пунктуации и переводит все в lower case
aBNTrimWS1()
{
#	((DEBUG)) && echo "[D:$FUNCNAME]"
	RET=$(echo "$1" | sed 's/[Ёё]/е/g; s/[”«»"“\.,=—?_…»–:-]//g; s/( /(/; s/[ ]\+/ /g; s/^ //g; s/./\L&/g')
	echo "$RET"
}

# Удаляет пробелы, символы пунктуации, автора из названия книги.
# Если есть серия книги, то удаляет номер серии.
# Переводит все в lower case
aBNTrimWS2()
{
#	((DEBUG)) && echo "[D:$FUNCNAME]"
	RET=$(echo "$1" | sed 's/[Ёё]/е/g; s/^[A-Za-яА-Яа-я]* //g; s/epub//; s/[”«»"“\.,=—?_…»–:-]//g; s/^[0-9]*//g; s/( /(/; s/[ ]\+/ /g; s/^ //g; s/./\L&/g')
	echo "$RET"
}

# Скрипт в текущем каталоге заменяет названия каталогов (имена авторов)
# с апострофами на единый для всех апостроф
#      о`генри -> О'Генри
aApostrofDir()
{
	for F in *; do 
		NF=$(echo "$F" | sed -e "s/\(^.\)['\`\"]\(.\)/\U\1\'\U\2/"); 
		if [ "$F" != "$NF"  ]; then 
			echo $NF; 
			if [ -d "$NF" ]; then
				echo "$F" == "$NF"
				#cp -R "$F/*" "$NF";
				#cp -R "$F";
			else
				mv "$F" "$NF"
			fi;
		fi; 
	done
}

########################################################################
#----------------------------------------------------------------------
#   Перемещает книги из одного каталога ($1) в другой ($2)
#   аналог команды mv
#   -------------------------------------------------------------------
aMoveBooksSameAutor()
{
	FROM="$1"
	TO="$2"
	
	if [ -d "$TO" ]; then
		# Такой каталог уже есть, 
		# будем перемещать только новые файлы большего размера, а
		# меньшие будем удалять.
				
		find "$FROM" -name '*.epub' | while IFS=$'\n' read -r FB; do
			# читаем все названия книг "$FROM"
			FBS=$(basename "$FB");
			FBS=$(aBNTrimWS2 "$FBS")
			find "$TO" -name '*.epub' | while IFS=$'\n' read -r TB; do
				TBS=$(basename "$TB");
				TBS=$(aBNTrimWS2 "$TBS")
				if [ "$FBS" = "$TBS" ]; then
					# Названия книг одинаковые
					FBSIZE=$(du -b "$FB" | cut -f 1)
					TBSIZE=$(du -b "$TB" | cut -f 1)
					echo "FROM=[$FBS] size=[$FBSIZE] [$FB]"
					echo "  TO=[$TBS] size=[$TBSIZE] [$TB]"
					if [ "$FBSIZE" -gt "$TBSIZE" ]; then
						..... нужно дописать
					fi
				else
					echo "Нужно дописать"
				fi
			done
		done

	else
		# Нового каталога не существет, можно просто переименовать.
		mv -v "$FROM" "$TO"
	fi
	
}

tCaseUpFL()
{
	foo="иВанов м"
	foo1="иВАНОВ м с"
	foo2="м иВАНов"
	foo3="м. иВАНов"
	foo4="м с иВАНов"
	foo5="м.с иВАНов"
	foo6="Иванов м.с.,петров с с"
	foo7="м.с иВАНов-сидоров"
	foo8="М. Р. иванов"
	foo9="сиДОРОВ к р"
 
	echo -e "\n$foo\n$foo1\n$foo2\n$foo3\n$foo4\n$foo5\n$foo6\n$foo7\n$foo8\n$foo9"; echo -e "\n$foo\n$foo1\n$foo2\n$foo3\n$foo4\n$foo5\n$foo6\n$foo7\n$foo8\n$foo9" |   \
		sed -e 's/./\L&/g; s/  / /g; s/  / /g; s/^./\U&/; s/[-\.]./\U&/g; s/ ./\U&/g; s/,./\U&/g; s/^\(.\) \(.\) /\1.\2. /; s/^\(.\) /\1. /; s/\(\..\) /\1. /g; s/ \(.\) \(.\)$/ \1.\2/g; s/\(\..\)$/\1\./; s/\(.\.\) \(.\.\) /\1\2 /; s/\( .\.\) \(.\)$/\1\2./g'
}
#----------------------------------------------------------------------
#   Рекурсивно обходит все подкаталоги с фамилиями авторов и переводит
#   первые буквы имени в верхний регистр 
#   -------------------------------------------------------------------
#   Ф.п. иВаноВ          -> Ф.П. Иванов
#   пЕтРов-вОдкиН п.П    -> Петров-Водкин П.П.

#   По текущему уровню библиотеки внутри одной буквы
aCaseUpFL_1L()
{
	pwd
	for D in *; do
		if [ -d "$D" ]; then
			ND=$(echo "$D" | sed -e 's/\xC2\xA0/ /g;s/./\L&/g; s/  / /g; s/^./\U&/; s/[-\.]./\U&/g; s/ ./\U&/g; s/,./\U&/g; s/^\(.\) \(.\) /\1.\2. /; s/^\(.\) /\1. /; s/\(\..\) /\1. /g; s/ \(.\) \(.\)$/ \1.\2/g; s/\(\..\)$/\1\./; s/\(.\.\) \(.\.\) /\1\2 /; s/\( .\.\) \(.\)$/\1\2./g; ')
			echo "[$D] -> [$ND]"
			if [ ! "$D" = "$ND" ]; then
				mv "$D" "$ND"
				echo -e "\\$L\\$D                       \r"
			fi
			((DEBUG)) && read -p "Press Enter" DUMMY
		fi
	done
}
#   По всей библиотеке (всем буквам) внутри одного языка
aCaseUpFL()
{
	# Обходим все буквы
	for L in *; do
		if [ -d "$L" ]; then
			cd "$L"
			aCaseUpFL_1L
			cd ..
		fi
	done
}

#----------------------------------------------------------------------
#  Рекурсивно обходит все подкаталоги с фамилиями авторов и убирает 
#  пробел между инициалами
#----------------------------------------------------------------------
#   Иванов Ф. П. -> Иванов Ф.П.

#   По текущему уровню библиотеки внутри одной буквы
aWrapAutorSp_1L()
{
	pwd
	for A in *; do 
		# инициалыв начале и в конце для ASCII и UTF-8
		NA=$(echo "$A" | sed "s/\xC2\xA0/ /g;s/ \(.\.\) \(.\.\)/ \1\2/;s/^\(.\.\) \(.\.\)/\1\2/")
		if [ "$NA" != "$A" ] ; then 
			((DEBUG)) && echo "[$A] - [$NA]"
			((DEBUG)) && read -p "Press Enter" DUMMY
			mv -v "$A" "$NA"; 
		fi;
	done;  
}

#   По всей библиотеке (всем буквам) внутри одного языка
aWrapAutorSp()
{
	for L in *; do 
		cd "$L"; 
		aWrapAutorSp_1L
		cd ..; 
	done
}

#----------------------------------------------------------------------
#  Меняет местами названия каталогов
#  Имя Фамилия -> Фамилия Имя
#  Отчество Фамилия Имя -> Фамилия Имя Отчество
#----------------------------------------------------------------------
aWrapAutorNOrder_1L()
{
	for DD in *; do
		F1=$(echo "$DD" | awk '{print $1;}')
		F2=$(echo "$DD" | awk '{print $2;}')
		F3=$(echo "$DD" | awk '{print $3;}')
		if [ ! "$F2" = "" ]; then
			if [ "$F3" = "" ]; then
				mv -v "$DD" "$F2 $F1"
			else
				mv -v "$DD" "$F2 $F3 $F1"
			fi
		fi
	done
}

aWrapAutorNOrder ()
{
	for L in *; do 
		cd "$L"; 
		aWrapAutorNOrder_1L
		cd ..
	done
}

#----------------------------------------------------------------------
# Переименовывает название книги
# Заменяет первое слово на фамилию, взятую из названия каталога
#----------------------------------------------------------------------
aBookWrap()
{
	
		for DD in *; do
			F1N=$(basename "$DD" | awk '{print $1;}')
			cd "$DD"
			echo "--------------------: $DD"
	
			for BB in *; do
				if [ -f "$BB" ]; then
					# это вложение первого уровня
					F1O=$(echo "$BB" | awk '{print $1;}')
					rename -v "s/^$F1O -/$F1N -/" "$BB"
					read -p "Press Enter" DUMMY
				else
					cd "$BB"
					for BBS in *; do
						if [ -f "$BBS" ]; then
							# это вложение второго уровня
							F1O=$(echo "$BBS" | awk '{print $1;}')
							rename -v "s/^$F1O /$F1N /" "$BBS"
							read -p "Press Enter" DUMMY
						fi
					done
					cd ..
				fi
			done
			cd ..
		done
}

#----------------------------------------------------------------------
#   Переводит первые буквы названия книги в верхний регистр
#   -------------------------------------------------------------------
#   Гавриленко - БРЕМЯ МЕРТВЫХ.epub -> Гавриленко - Бремя мертвых.epub
aWrapBookName()
{
	for F in *;  do 
		NF=$(echo "$F" | sed 's/./\L&/g; s/^./\U&/g; s/[\.!?-]\s*./\U&\E/g; s/Epub/epub/g'); 
		if [ ! "$F" = "$NF" ]; then
			mv "$F" "$NF"; 
		fi
	done
}

#----------------------------------------------------------------------
#   Перемещает новых авторов, которых нет в целевой 
#   библиотеке в целевую библиотеку
#	На входе получает 2 аргумента:
#		$1 - FROM
#		$2 - TO
aMoveNewAutor()
{
	DEBUG=1
	local FROM="$1"
	local TO="$2"
	((DEBUG)) && echo "[$FROM] -> [$TO]"
	# обходим всю библиотеку
	X=0
	T=0
	for L in ${FROM}/*; do
		if [ -d "$L" ]; then
			NL=$(basename "$L")
			for A in $L/*; do
				((T++))
				if [ -d "$A" ]; then
					NA=$(basename "$A")
					if [ ! -d "$TO/$NL/$NA" ]; then
						mv -v "$A" "$TO/$NL"
						((X++))
					fi
				fi
			done
		fi
	done
	echo $X/$T
	DEBUG=0
}

#----------------------------------------------------------------------
#  Сравнивает названия книг из новой библиотеки и целевой.
#  Удаляет повторы из новой.
#  Предварительно из названия убираются все символы пунктуации 
#    и пробельные символы
#	На входе получает 2 аргумента:
#		$1 - FROM
#		$2 - TO
# Время работы ~15h
aDelSameBook()
{
	local FROM="$1"
	local TO="$2"
	# обходим всю библиотеку
	for L in $FROM/*; do
		if [ -d "$L" ]; then
			NL=$(basename "$L")
			for A in $L/*; do
				if [ -d "$A" ]; then
					NA=$(basename "$A")
					find "$FROM/$NL/$NA" -name '*.epub' | while IFS=$'\n' read -r NBOOKFP; do
						NB=$(basename "$NBOOKFP")
						NB=$(aBNTrimWS "$NB")
						find "$TO/$NL/$NA" -name '*.epub' | while IFS=$'\n' read -r OBOOKFP; do
							OB=$(basename "$OBOOKFP")
							OB=$(aBNTrimWS "$OB")
#	            			echo -e "\n$NB\n$OB"
							if [ "$NB" = "$OB" ]; then
								echo "[FOUND] $OB  $NBOOKFP"
								rm "$NBOOKFP"
							fi
						done
					done
				fi
			done
		fi
	done
}	

#----------- Что то здесь работает не так. Удаление закоментировано ----
#  Сравнивает названия книг в целевой библиотеке и удаляет повторы.
#  Предварительно из названия убираются все символы пунктуации 
#    и пробельные символы
aOrgDelSameBook()
{
	local TO="$1"
	# обходим всю библиотеку
	for L in $TO/*; do
		if [ -d "$L" -a ! "$L" = "$TO/_" ]; then
			NL=$(basename "$L")
			echo "$L"
			for A in $L/*; do
				if [ -d "$A" ]; then
					NA=$(basename "$A")
					echo "$A"
					find "$TO/$NL/$NA" -name '*.epub' | while IFS=$'\n' read -r I; do
						find "$TO/$NL/$NA" -name '*.epub' | while IFS=$'\n' read -r J; do
							if [ "$I" != "$J" ]; then
								NI=$(basename "$I")
								NI=$(aBNTrimWS "$NI")
								NJ=$(basename "$J")
								NJ=$(aBNTrimWS "$NJ")
#								echo "$NJ"
#                				[ "$NI" = "$NJ" ] && rm "$J"
								[ "$NI" = "$NJ" ] && echo -e "[I duplicate] $I\n[J duplicate] $J\n"
							fi
						done
					done
				fi
			done
		fi
	done
}


#----------------------------------------------------------------------
#  Удалаяем пустые каталоги
#   $1 - путь к библиотеке
aDelEmptyDir()
{
	echo "Deleting empty Dir in $1"
	find "$1" -empty -type d -delete
}

#----------------------------------------------------------------------
#  Сравнивает имена книг двух авторов. 
#  Если есть хотя бы одна одинаковая книга, то это один и тот же автор
#  В этом случае возвращает 1
#  Если авторы разные, то возвращает 0
#  Функция принимает 2 аргумента:
#  $1 - путь к книгам первого автора
#  $2 - путь к книгам второго автора
aIsSameAutor()
{
	DEBUG=0
	RETSAMEAUT=/tmp/retsameautor
	((DEBUG)) && echo "[D:$FUNCNAME]"
	((DEBUG)) && echo "[D:$LINENO] [$1]"
	((DEBUG)) && echo "[D:$LINENO] [$2]"
	echo 0 > "$RETSAMEAUT"
	find "$1" -type f -name "*.epub" -print | while IFS=$'\n' read -r BOOKI; do
      BI=$(basename "$BOOKI")
      BI=$(aBNTrimWS "$BI")
      find "$2" -type f -name "*.epub" -print | while IFS=$'\n' read -r BOOKJ; do
        BJ=$(basename "$BOOKJ")
        BJ=$(aBNTrimWS "$BJ")
        ((DEBUG)) && echo "[D:$LINENO] [$BI]"
        ((DEBUG)) && echo "[D:$LINENO] [$BJ]"
        if [ "$BI" = "$BJ" ]; then
          echo 1 > "$RETSAMEAUT"
        fi
      done
    done
    DEBUG=1
    cat $RETSAMEAUT
}

aMoveBooks()
{
	DEBUG=0
	((DEBUG)) && echo "[D:$FUNCNAME]"
	# Сохраняем аргументы
	local A1=$1; 
	local A2=$2
	local LENA1=0;
	local LENA2=0;

	# Определяем "откуда" и "куда"

	# Если в конце каталога пробел, то будем этот каталог 
	#   уничтожать. Это "Откуда"
	LENA1=${#A1}
	((LENA1--))
	CI=${A1:LENA1:1}
	LENA2=${#A2}
	((LENA2--))
	CJ=${A2:LENA2:1}
	if [ "$CI" = " " ]; then
		FROM=$A1; DEST=$A2
	else
		if [ "$CJ" = " " ]; then
			FROM=$A2; DEST=$A1
		else
			# Иначе источник - более короткий каталог
			if [ $LENA1 -lt $LENA2 ]; then
				FROM=$A1; DEST=$A2
			else
				FROM=$A2; DEST=$A1
			fi
		fi
	fi
	((DEBUG)) && echo "[D:$LINENO] FROM=[$FROM]"
	((DEBUG)) && echo "[D:$LINENO] DEST=[$DEST]"

	# Удаляем одинаковые книги.
	RETFOUNDBOOK=/tmp/retfoundbook
	echo 0 > $RETFOUNDBOOK
	find "$FROM" -type f -name "*.epub" -print | while IFS=$'\n' read -r BOOK_FROM; do
		B_F=$(basename "$BOOK_FROM")
		B_F=$(aBNTrimWS2 "$B_F")
		find "$DEST" -type f -name "*.epub" -print | while IFS=$'\n' read -r BOOK_DEST; do
			B_D=$(basename "$BOOK_DEST")
			B_D=$(aBNTrimWS2 "$B_D")
			((DEBUG)) && echo "[D:$LINENO] [$B_F] [$FROM]"
			((DEBUG)) && echo "[D:$LINENO] [$B_D] [$DEST]"
			if [ "$B_F" = "$B_D" ]; then
				# Это одна и та же книга. Стираем и ставим флаг,
				# что это один и тот же автор
				echo 1 > $RETFOUNDBOOK
				echo -e "Удаляю -------------------------------------------------------------------------"
				rm -v "$BOOK_FROM"
			fi
		done
	done
	
	# Были одинаковые книги. Автор один и тот же. 
	# Перемещаем
	FOUND=$(cat $RETFOUNDBOOK)
	if [ "$FOUND" -eq 1 ]; then
		HAVEBOOKS=$(ls)
		if [ -n "$HAVEBOOKS" ]; then
			if [ -d "$FROM" ]; then
				echo -e "Перемещаю ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				cp -R -v "$FROM/*" "$DEST"
				rm -r "$FROM"
			fi
		fi
	fi
	DEBUG=0
}

#----------------------------------------------------------------------
#  Сравнивает имена авторов в целевой библиотеке и мержит повторы.
#   $1 - путь к библиотеке
aMergeDupAutors()
{
	DEBUG=0
	local LIB="$1"
	((DEBUG)) && echo "[D:$FUNCNAME]"
	# обходим всю библиотеку
	for L_I in $LIB/*; do
		L=$(basename "$L_I")
		echo "$L --                                                    "
		if [ -d "$LIB/$L" ]; then
			# обходим всех авторов с именем AI
			for A_I in $LIB/$L/*; do
				#printf "%s                         \r" "$A_I"
				if [ -d "$A_I" ]; then
					BA_I=$(basename "$A_I")
					FN_I=$(echo "$BA_I" | awk '{print $2}')
					LN_I=$(echo "$BA_I" | awk '{print $1}')
					F_LETTER_FN=${FN_I:0:1}
					((DEBUG)) && S="$LN_I $F_LETTER_FN"
					find "$LIB/$L" -maxdepth 1 -type d -name "$LN_I ${F_LETTER_FN}*" -print | while IFS=$'\n' read -r LIKE_AUTOR; do
						local SAME_AUTOR=0
						if [ ! "$LIKE_AUTOR" = "$A_I" ]; then
							((DEBUG)) && echo "[D:$LINENO] $S == [$LIKE_AUTOR]"
							SAME_AUTOR=$(aIsSameAutor "$A_I" "$LIKE_AUTOR")
							((DEBUG)) && echo -e "\n[D:$LINENO] SAME_AUTOR=$SAME_AUTOR"
							if [ $SAME_AUTOR = 1 ]; then
								aMoveBooks "$A_I" "$LIKE_AUTOR"
							fi
						fi
					done
				fi
			done
		fi
	done
	DEBUG=0
}

#----------------------------------------------------------------------
# Конвертирует библиотеку из win1251 в utf8
aLibToUtf8()
{
	local NB;
	local RC;
	
	echo "Convert to utf8 in $1"
    cd "$1"
    
	# Обходим все книги из update
	for NB in *.fb2;
	do
	    # Конвертируем в utf-8 и исправляем ошибки
	    xmllint --recover --format --encode "UTF-8" "$NB" -o "${NB}.utf8"
	    RC=$?
	    
	    if [ "$RC" == 0 ]; then	# Если сконвертировлось без ошибок, 
			rm "$NB"			# то стираем исходный файл
		else
			mv "$NB" "$UPD_ERR"	# если с ошибками, то перемещаем
		fi
		echo -n -e "$NB                                           \r"
	done
}

#----------------------------------------------------------------------
# Переименовывает книги в соответствии со следующими шаблонами
# Отдельная книга
#        <Last_Name> - <Title_Name>.epub
# Книга из серии, где NN - номер книги в серии
#        <Last_Name> <NN> <Title_Name>.epub
# Раскладывает книги по каталогам, как в библиотеке Траума
# Исчточник - новая библиотека LibRusEc или в формате fb2.
# Исходные книги лежат в одном каталоге и имеют цифровые имена
aSaveLikeTraum()
{
	echo "Convert utf8 to ePub an move to $UPD_EPUB_RU"

	# При включенном выводе отладочной информации скорость 
	# работы замедляется примерно в 6-10 раз
	DEBUG=0
	TSTSPEED=0
	# Обходим все книги из update
	for NB in *.utf8;
	do
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		FN_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:author/fb:first-name/text()' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/^ //; s/ $//;')
		FN_NEW=$(echo $FN_NEW | awk '{ print $1 }' | sed "s/./\L&/g; s/^./\U&/")

		MN_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:author/fb:middle-name/text()' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/^ //; s/ $//;')
		MN_NEW=$(echo $MN_NEW | awk '{ print $1 }' | sed "s/./\L&/g; s/^./\U&/")

		LN_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:author/fb:last-name/text()' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/^ //; s/ $//;')
		LN_NEW=$(echo $LN_NEW | awk '{ print $1 }' | sed "s/./\L&/g; s/^./\U&/")
		if [ -z "$LN_NEW" ]; then
			#Если поле фамилии пустое
			LN_NEW="$FN_NEW"
			FN_NEW=""
		fi
		TITLE_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:book-title/text()' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/^ //; s/\//-/g; s/ $//;')
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N

		# Если название книги только в верхнем регистре, то делаем первую
		# букву заглавной, а все остальные маленькими.
		if ! [[ "$TITLE_NEW" =~ [^А-Я0-9\ \.,-] ]]; then 
			TITLE_NEW=${TITLE_NEW,,}; 
			TITLE_NEW=($TITLE_NEW); 
			TITLE_NEW=${TITLE_NEW[@]^}; 
		fi

		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		NAME_SEQ_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:sequence/@name' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/\"//g; s/ name=//; s/^ //; s/ $//;')
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		NUMBER_SEQ_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:sequence/@number' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/\"//g; s/ number\=//; s/^ //; s/ $//;')
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		LANG_NEW=$(echo -e 'setns fb=http://www.gribuser.ru/xml/fictionbook/2.0\ncat /fb:FictionBook/fb:description/fb:title-info/fb:lang/text()' | xmllint --noout --shell "$NB" | sed '/^\/ >/d; /^ -------/d; s/<[^>]*.//g; s/^ //; s/ $//;')
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		if [ -z "$LANG_NEW" ]; then LANG_NEW="unknown"; fi
		((DEBUG)) && echo [$NB]:[$FN_NEW] [$MN_NEW] [$LN_NEW] [$TITLE_NEW] [$NAME_SEQ_NEW] [$NUMBER_SEQ_NEW] [$LANG_NEW]
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N

		# Формируем каталог книги
		AUTOR="$LN_NEW"
		if [ -n "$FN_NEW" ]; then AUTOR="$AUTOR $FN_NEW"; fi
		if [ -n "$MN_NEW" ]; then AUTOR="$AUTOR $MN_NEW"; fi
		AUTOR=$(echo "$AUTOR" | sed -e 's/./\L&/g; s/  / /g; s/  / /g; s/^ //; s/^./\U&/; s/[-\.]./\U&/g; s/ ./\U&/g; s/,./\U&/g; s/^\(.\) \(.\) /\1.\2. /; s/^\(.\) /\1. /; s/\(\..\) /\1. /g; s/ \(.\) \(.\)$/ \1.\2/g; s/\(\..\)$/\1\./; s/\(.\.\) \(.\.\) /\1\2 /; s/\( .\.\) \(.\)$/\1\2./g')
		
		if [ -z "$AUTOR" ]; then
			AUTOR="Unknown"
			LN_NEW="Unknown"
		fi
		((DEBUG)) && echo AUTOR=[$AUTOR]
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		
		DEST_DIR="$UPD_EPUB_RU/$LANG_NEW/${LN_NEW:0:1}/$AUTOR"

		if [ -n "$NAME_SEQ_NEW" ]; then
			DEST_DIR="$DEST_DIR/$NAME_SEQ_NEW"
			SEQ=$(printf "%02d" "${NUMBER_SEQ_NEW#0}")
			BOOK_NAME="$LN_NEW $SEQ $TITLE_NEW"
		else
			BOOK_NAME="$LN_NEW - $TITLE_NEW"
		fi
		
		((DEBUG)) && echo "[$NB]:$DEST_DIR/$BOOK_NAME"
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N
		
		if [ ! -d "$DEST_DIR" ]; then 
			mkdir -p "$DEST_DIR"; RES1=$?
		fi
		
		if [ -f "$DEST_DIR/$BOOK_NAME.epub" ];then
			# если такая книга уже есть, то стираем кандидат
			rm "$NB"
		else
			# такой книги в бибилиотеке кандидате нет. конвертируем
			mv  "$NB" "$BOOK_NAME.fb2"; RES2=$?
		
			if [[ $RES1 -eq 1 ]] || [[ $RES2 -eq 1 ]]; then
				# если с ошибками, то перемещаем в каталог ошибок
				mv "$NB" "$UPD_ERR"
			else
				# Конвертируем книгу в Epub и сохраняем книгу в новый каталог
				$FB2CONV --profile liberation --output-format epub --delete-source-file --output-dir "$DEST_DIR" "$BOOK_NAME.fb2"
			fi
		fi
		((TSTSPEED)) && echo -n -e "[$LINENO]:" && date +%s%1N

	done
	DEBUG=0
	TSTSPEED=0

}

SOURCE="$UPD_FB2"
DEST="$LIB_RU"

echo "Конвертируем из win1251 в utf-8"
aLibToUtf8 "$SOURCE"

echo "Конвертируем из fb2 в epub и раскладываем книги в структуру аля Traum"
aSaveLikeTraum

#echo "Удаляю в библиотеке кандидате пустые каталоги"
#aDelEmptyDir "$SOURCE"

#echo "Перемещаем новых авторов"
#aMoveNewAutor "$SOURCE" "$DEST"

#echo "Удаляю в библиотеке кандидате дубликаты с целевой библиотекой"
#aDelSameBook "$SOURCE" "$DEST"

#echo "Удаляю в библиотеке кандидате пустые каталоги"
#aDelEmptyDir "$SOURCE"

# Теперь нужно переместить все оставшиеся книги в целевую библиотеку
#echo "Перемещаю все оставшиеся книги в целевую библиотеку"
#cp -R $SOURCE/* $DEST
#rm -r $SOURCE


#echo "Удаляю в библиотеке одинаковые книги внутри одного автора"
# В функции ошибка. Не работает. Переъходим к следующей функции.
#aOrgDelSameBook "$DEST"

#Объединяю одинаковых авторов
#aMergeDupAutors "$DEST"

#==================================================================
#aMoveBooksSameAutor "Ф. Лекси" "Ф. Лекси"
