{#
	FILE :top.tpl
	DATE :2017.12.20
	DESCRIPTION :トップページテンプレート
	NAME :Hikaru Yoshida
#}

{# ベーステンプレートを継承 #}
{% extends "base.tpl" %}

{# <title></title>内の記述 #}
{% block title %}
	トップページ
{% endblock %}

{# <head></head>内の記述 #}
{% block lib %}
	{{ super() }}
{% endblock %}

{# ページのヘッダー #}
{% block header %}
	{{ super() }}
{% endblock %}

{# ページのコンテンツ #}
{% block content %}
	<h2>What this?</h2>
	校内の各教室に設置されたセンサーによって収集された値をグラフやマップにして出力します。
{% endblock %}

{# ページのフッター #}
{% block footer %}
	{{ super() }}
{% endblock %}