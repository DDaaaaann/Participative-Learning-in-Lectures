//<!--
var eggsFound = 0;
var bigEggsFound = 0;
var i = 0;

function findTheEgg() {
    eggsFound++;
    if (eggsFound == 7) {
        logoBlink();
    }
}

function logoBlink() {
    setTimeout(function () {
        $("#logo").toggleClass("logo");
        $("#logo").toggleClass("greenlogo");
        i++;
        if (i < 10) {
            logoBlink();
        }
    }, 250)
}

function playclip() {
    if (eggsFound > 6) {
        $("#wav").attr("src", "/media/audio/PILS" + bigEggsFound +".wav");
        var audio = document.getElementsByTagName("audio")[0];
        audio.load();
        audio.play();
    }
}

function pauseclip() {
    if (eggsFound > 6) {
        var audio = document.getElementsByTagName("audio")[0];
        audio.pause();
    }
}

function donePlaying() {
    bigEggsFound++;
    if (bigEggsFound == 4) {
        setMask(1, 0.8);
    }
}

function setMask(closable, opacity)
{
    $('.boxes').prepend("<div class=\"mask\"></div>");
    //Get the screen height and width
    var maskHeight = $(document).height();
    var maskWidth = $(window).width() + 25;
    //Set height and width to mask to fill up the whole screen
    $('.mask').css({'width':maskWidth,'height':maskHeight});

    //transition effect
    $('.mask').fadeIn(1000);
    $('.mask').fadeTo("slow", opacity);

    if (closable) {
        $('.mask').click(function () {
            $(this).hide();
            $('.window, .close').hide();
        });

        $(document).keyup(function(e) {
            if(e.keyCode === 27) {
                $('.window, .close, .mask').hide();
            }
        });
    }
}

//-->


