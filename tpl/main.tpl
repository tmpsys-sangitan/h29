{#
	FILE :main.tpl
	DATE :2017.12.20
	DESCRIPTION :メインページテンプレート
	NAME :Hikaru Yoshida
#}

{# ベーステンプレートを継承 #}
{% extends "tpl/base.tpl" %}

{# <title></title>内の記述 #}
{% block title %}
	トップページ
{% endblock %}

{# <head></head>内の記述 #}
{% block lib %}
	{{ super() }}
	{# jqueryを読み込み #}
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
	{# jquery-uiを読み込み #}
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
	{# jquery-ui-datepickerを読み込み #}
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1/i18n/jquery.ui.datepicker-ja.min.js"></script>
	{# google chart toolsを読み込み #}
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
	{# graph.jsを読み込み #}
    <script type="text/javascript" src="./js/graph.js"></script>
	{# jsondata.jsを読み込み #}
    <script type="text/javascript" src="./js/jsondata.js"></script>
{% endblock %}

{# ページのヘッダー #}
{% block header %}
	{{ super() }}
{% endblock %}

{# ページのコンテンツ #}
{% block content %}
	{# グラフ #}
	<div id="graphField">Now Loading ...</div>
	<script type="text/javascript">
		mapid_list = [
			"test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8",
			"test9", "test10", "test11", "test12", "test13", "test14", "test15", "test16"
		]

		var j = new Graph(mapid_list, "2017/11/22 00:00:00 +0900", "day");
	</script>

	{# What this? #}
	<div id="content">
		<h2>What this?</h2>
		産業技術短期大学校の各教室に設置されたセンサーによって、収集された値をグラフやマップにして出力します。
	</div>
{% endblock %}

{# ページのフッター #}
{% block footer %}
	{{ super() }}
{% endblock %}
