/**
 * Created by Asimple on 2017/11/26.
 */
function swapFromToCity(){
    var from = document.getElementById("from-city").value;
    var to = document.getElementById("to-city").value;
    if( from!="" && to!="" ) {
        $("#from-city").val(to);
        $("#to-city").val(from);
    }
};