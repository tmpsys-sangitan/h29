var HeatMap = {
    searchSensor: function(){
        /*
         * searchSensor .snsrクラスを検索して温度の表示と背景色の変更を行う
         * id : 変更する要素
         * temp : 温度
         */
        jQuery('.snsr').each(function(){
            var temp = Math.floor(Math.random()*35);
            HeatMap.setNewlabel(this, temp);
            HeatMap.setBGColor(this, temp);
        });
    },

    setNewlabel: function(id, temp){
        /*
         * setNewlabel 温度とラベルを表示
         * id : 変更する要素
         * temp : 温度
         */
        $(id).html($(id).text() + "<br>" + temp + "℃");
    },

    setBGColor: function(id, temp){
        /*
         * setBGColor 温度に応じて指定された要素の背景色を変更する
         * id : 変更する要素
         * temp : 温度
         */
        $(id).css('background-color', hsv(220-220*temp/35, 0.5, 1));
    }
}

function hsv(h,s,v){
    var f=h/60,i=f^0,m=v-v*s,k=v*s*(f-i),p=v-k,q=k+m;
    return '#'+c16([v,p,m,m,q,v][i]*255^0)+c16([q,v,v,p,m,m][i]*255^0)+c16([m,m,q,v,v,p][i]*255^0);
}

function c16( c10 ){
    var c16 = '0'+c10.toString(16);
    return c16.substr(c16.length-2);
}
