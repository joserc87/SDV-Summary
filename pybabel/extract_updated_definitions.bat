pybabel extract -F ../sdv/babel.cfg -k lazy_gettext -o ../sdv/messages.pot ../sdv
pybabel update -i ../sdv/messages.pot -d ../sdv/translations
pause