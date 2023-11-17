$file = ".\vepkardb-20230201-copy.sql"
$find = 'values (1, "admin@test.ru", password("admin"))'
$replace = "values (1, 'admin@test.ru', password('admin'))"

(Get-Content $file).replace($find, $replace) | Set-Content $file