{# FILE :main.tpl DATE :2017.12.20 DESCRIPTION :メインページテンプレート NAME :Hikaru Yoshida #} {# ベーステンプレートを継承 #} {% extends "tpl/base.tpl"
%} {#
<title></title>内の記述 #} {% block title %} トップページ {% endblock %} {#

<head></head>内の記述 #} {% block lib %} {{ super() }} {# jquery v3.3.1を読み込み #}
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script> {# jquery-ui v1.12.1を読み込み #}
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
<link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"> {# jquery-ui-datepickerを読み込み #}
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1/i18n/jquery.ui.datepicker-ja.min.js"></script> {# google chart toolsを読み込み #}
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> {# graph.jsを読み込み #}
<script type="text/javascript" src="./js/graph.js"></script> {# map.jsを読み込み #}
<script type="text/javascript" src="./js/map.js"></script> {# ページ固有設定 #}
<script>
	var url = '//tmpsys-sangitan.appspot.com/'

	$(function () {
		DatePicker.init('#select_date');
		SelectLocation.init('#select_loc');
		Graph.init('#graphField', '#graphInfo');
		HeatMap.init();
	});
</script> {% endblock %} {# ページのヘッダー #} {% block header %} {{ super() }} {% endblock %} {# ページのコンテンツ #} {% block content %}
<div id="content">
	{# オプション #}
	<div id='graphOptionList'>
		<div id='graphOption'>
			日付:
			<input type="text" id="select_date" />
		</div>
		<div id='graphOption'>
			期間:
			<select id="select_period">
				<option value="day">日間</option>
			</select>
		</div>
		<div id='graphOption'>
			場所:
			<select id="select_loc">
				<option value="none">全て</option>
				<option value="3f">3階</option>
			</select>
		</div>
		<div id='graphOption'>
			種類:
			<select id="select_type">
				<option value="temp">温度</option>
			</select>
		</div>
	</div>
	{# グラフ #}
	<div id="graphInfo"></div>
	<div id="graphField"></div>
</div>

{# マップ #}
<script>
</script>
<div id="mapField">
	<h2>3F</h2>
	<table id="map">
		<tr>
			<td class="snsr s2cr">S2教室</td>
			<td class="corr"></td>
			<td class="snsr t1lab" colspan="2">T1実習室</td>
			<td class="less"></td>
			<td class="less"></td>
			<td class="less"></td>
			<td class="corr"></td>
			<td class="less"></td>
			<td class="snsr elec" rowspan="3">電子工作室</td>
		</tr>
		<tr>
			<td class="corr" colspan="9"></td>
		</tr>
		<tr>
			<td class="snsr 3fsemi">3Fゼミ室</td>
			<td class="snsr net" colspan="2">ネットワーク
				<br>実習室</td>
			<td class="snsr t2lab" colspan="2">T2実習室</td>
			<td class="snsr img" colspan="2">画像処理室</td>
			<td class="snsr t2cr">T2教室</td>
			<td class="less"></td>
		</tr>
	</table>
</div>
<div id="mapField">
	<h2>2F</h2>
	<table id="map">
		<tr>
			<td class="corr"></td>
			<td class="less"></td>
			<td class="corr"></td>
			<td class="snsr s2lab" colspan="2">S2実習室</td>
			<td class="snsr 2ftr">教官室</td>
			<td class="less"></td>
			<td class="less"></td>
			<td class="corr"></td>
			<td class="snsr wslab" rowspan="3">WS実習室</td>
		</tr>
		<tr>
			<td class="corr" colspan="9"></td>
		</tr>
		<tr>
			<td class="corr"></td>
			<td class="snsr s1lab" colspan="2">S1実習室</td>
			<td class="snsr s1cr">S1教室</td>
			<td class="snsr t1cr">T1教室</td>
			<td class="corr"></td>
			<td class="less" colspan="2"></td>
			<td class="snsr 2fsemi">F2ゼミ室</td>
		</tr>
	</table>
</div>
<div id="mapField">
	<h2>1F</h2>
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
			<td class="less"></td>
			<td class="less" rowspan="3"></td>
		</tr>
		<tr>
			<td class="corr" colspan="9"></td>
		</tr>
		<tr>
			<td class="less"></td>
			<td class="snsr 1ftr" colspan="2">職員室</td>
			<td class="less"></td>
			<td class="less"></td>
			<td class="less" colspan="2"></td>
			<td class="corr"></td>
			<td class="less"></td>
		</tr>
	</table>
</div>

{# What this? #}
<div id="content">
	<h2>What this?</h2>
	茨城県立IT短大の各教室に設置されたセンサーによって収集した値を、グラフやマップで表示します。
</div>
{% endblock %} {# ページのフッター #} {% block footer %} {{ super() }} {% endblock %}
