
$(document).ready(function(){

    $(".cat-link").click(function(e){
        e.preventDefault();
        //$("#btn-test").text($(this).text());

        var btnID = "#btn-cat_"+$(this).attr("data-a-cat");
        console.log(btnID);
        $(btnID).text($(this).text());
        
        console.log("FUCK YOU, JS");
    });

});


