{#
    FILE :top.tpl
    DATE :2017.12.20
    DESCRIPTION :アップロードページテンプレート
    NAME :Hikaru Yoshida
#}
<!doctype html>

<html>

<head>
    <title>upload</title>
</head>

<body>
    <form method="post" action="/upload">
        <input type="text" name="id" />
        <br>
        <input type="text" name="date" />
        <br>
        <input type="text" name="fi" />
        <br>
        <input type="text" name="bv" />
        <br>
        <input type="text" name="val" />
        <br>
        <input type="text" name="ad" />
        <br>
        <button name="btn" type="submit">send</button>
    </form>
</body>

</html>
