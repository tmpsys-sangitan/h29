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
	<div id="content">
	<div id="graphField">Now Loading ...</div>
	<script type="text/javascript">
		label_list = [
			"テストデータ1", "テストデータ2", "テストデータ3", "テストデータ4",
			"テストデータ5", "テストデータ6", "テストデータ7", "テストデータ8",
			"テストデータ9", "テストデータ10", "テストデータ11", "テストデータ12",
			"テストデータ13", "テストデータ14", "テストデータ15", "テストデータ16"
		]

		mapid_list = [
			"test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8",
			"test9", "test10", "test11", "test12", "test13", "test14", "test15", "test16"
		]

		var j = new Graph(mapid_list, "2017/11/22 00:00:00 +0900", "day");
	</script>

	{# マップ #}
	<div id="mapField">
		3F
		<table id="map">
			<tr>
				<td class="snsr s2cr">S2教室</td>
				<td class="corr"></td>
				<td class="snsr t1lab" colspan="2">実習室</td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="corr"></td>
				<td class="snsr elec" rowspan="3">電子工作室</td>
			</tr>
		<tr>
			<td class="corr" colspan="8"></td>
		</tr>
			<tr>
				<td class="snsr 3fsemi">3Fゼミ室</td>
				<td class="snsr net" colspan="2">ネットワーク<br>実習室</td>
				<td class="snsr t2lab" colspan="2">実習室</td>
				<td class="snsr img" colspan="2">画像処理室</td>
				<td class="snsr t2cr">T2教室</td>
			</tr>
		</table>
	</div>
		<table id="map">
			<tr>
				<td class="less"></td>
				<td class="corr"></td>
				<td class="snsr s2lab" colspan="2">実習室</td>
				<td class="snsr 2ftr">教官室</td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="corr"></td>
				<td rowspan="3">UNIX</td>
			</tr>
			<tr>
				<td class="corr" colspan="8"></td>
			</tr>
			<tr>
				<td class="snsr s1lab" colspan="2">実習室</td>
				<td class="snsr s1cr">S1教室</td>
				<td class="snsr t1cr">T1教室</td>
				<td class="corr"></td>
				<td class="less" colspan="2"></td>
				<td class="snsr 2fsemi">F2ゼミ室</td>
			</tr>
		</table>
		<br>
		<table id="map">
			<tr>
				<td class="less"></td>
				<td class="corr"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="corr"></td>
				<td class="less" rowspan="3"></td>
			</tr>
			<tr>
				<td class="corr" colspan="8"></td>
			</tr>
			<tr>
				<td class="less"></td>
				<td class="snsr 1ftr" colspan="2">職員室</td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
				<td class="less"></td>
			</tr>
		</table>

	{# What this? #}
	<div id="content">
		<h2>What this?</h2>
		産業技術短期大学校の各教室に設置されたセンサーによって収集された値をグラフやマップにして出力します。
	</div>
{% endblock %}

{# ページのフッター #}
{% block footer %}
	{{ super() }}
{% endblock %}
