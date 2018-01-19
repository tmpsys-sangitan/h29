{#
	FILE :base.tpl
	DATE :2017.12.20
	DESCRIPTION :ベーステンプレート
	NAME :Hikaru Yoshida
#}
<!doctype html>

<html>

<head>
	{% block lib %}
	{# 文字コードをUTF-8に固定 #}
	<meta charset="UTF-8">
	{# タイトル #}
	<title>{% block title %}{% endblock %} - 県立IT短大 センサ管理システム</title>
	{# スタイルシートを読み込み #}
	<link rel="stylesheet" type="text/css" href="./css/main.css">
	{% endblock %}
</head>

<body>
	<div id="header">
		{% block header %}
		<img src="favicon.ico">
		<header>
			<h2>県立IT短大 センサ管理システム</h1>
			<p>Ibaraki Prefectural Junior College of Industrial Technology</p>
		</header>
		{% endblock %}
	</div>

	<div id="menu">
		<ul>
			<li><a href="./">Top</a></li>
			<li><a href="./graph">Graph</a></li>
			<li><a href="./map">Map</a></li>
		</ul>
	</div>

	<div id="content">
		{% block content %}
		{% endblock %}
	</div>

	<div id="footer">
		{% block footer %}
		&copy; Copyright 2018 by <a href="http://www.ibaraki-it.ac.jp/">Ibaraki Prefectural Junior College of Industrial Technology</a>. All rights reserved.
		{% endblock %}
	</div>
</body>

</html>