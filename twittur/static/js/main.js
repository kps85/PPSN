// Fullpage Height

function fph() { 
    var vph = $(window).height();
    $('.full-page').css({'minHeight':vph + "px"});
}

var tspeed = 500;

// First Time Use
function initFtu() {
	if($("#ftu").length <= 0) return;
	
	$(".box h2.toggle").click(function() {
		var show = $(this).attr('id').replace("show_","");
		$(".toggleItem").hide();
		$("#" + show).show();
		$("h2.active").removeClass("active");
		$(this).addClass("active");
	});
	
	$(".box .forgot").click(function() {
		$(this).closest(".box").fadeOut(tspeed, function() {
			$(".forgotBox").fadeIn(tspeed);
		});
	});
	
	$(".forgotBox .forgotBack").click(function() {
		$(this).closest(".box").fadeOut(tspeed, function() {
			$(".loginBox").fadeIn(tspeed);
		});
	})
	
}

// Menue
var windowWidth = $(window).width();

function initMenu() {
	var $menuOpener = $("<a>", {'class':'menuOpener', 'href':'javascript:;'});
	var $patty = $("<div>", {'class':'patty'});
	for(var i = 0; i <3; i++) {
		$patty.clone().appendTo($menuOpener);
	}
	
	
	$menuOpener.appendTo("#head");
	
	$(".menuOpener, .menuOpener > *").click(function() {

		var $a = $("#aside");
		if($a.is(":hidden")) {
			$a.show();
			$a.animate({'left':0}, 300);
		} 
	});
	
	
	var $menuCloser = $("<a>", {'class':'menuCloser', 'html':'Zur&uuml;ck'});
	$menuCloser.appendTo("nav");
	
	$(".menuCloser").click(function() {
		var $a = $("#aside");
		if($a.is(":visible") && $menuOpener.is(":visible")) {
			
			$a.animate({'left':'-100%'}, 300, function() {
				$a.hide();
			});
		} 
	});
	
	
	var menuOpenerWasVisible = false;
	if($(".menuOpener").is(":visible")) {
		menuOpenerWasVisible = true;
	}
	
	$(window).resize(function() {
		if($(window).width() == windowWidth) return
		windowWidth = $(window).width();
		if($(".menuOpener").is(":hidden") && menuOpenerWasVisible) {
			$("#aside").css({'left':'0'})
			$("#aside").show();
			menuOpenerWasVisible = false;
		} else if($(".menuOpener").is(":visible") && !menuOpenerWasVisible) {
			$("#aside").css({'left':'-100%'})
			$("#aside").hide();
			menuOpenerWasVisible = true;
		}
	})
}

var hideInfo = function(e) { $(e).parent("div").hide(); }

$('body').delegate('#ftu, #ftu input[type=text], #ftu input[type=password]', 'mousemove', function(e) {
	($('#login input[type=text]').val().replace( /\s/g, "") != '' && $('#login input[type=password]').val().replace( /\s/g, "") != '') ? 
																							$('#login input[type=submit]').prop("disabled", false) :
																							$('#login input[type=submit]').prop("disabled", true);
	($('#name').val().replace( /\s/g, "") != '' && $('#email').val().replace( /\s/g, "") != '' &&
	 $('#password').val().replace( /\s/g, "") != '' && $('#ack_password').val().replace( /\s/g, "") != '') ? 
																							$('#register input[type=submit]').prop("disabled", false) :
																							$('#register input[type=submit]').prop("disabled", true);
});

$('#newMessage').delegate('textarea', 'keyup', function(e) {
	($(this).val().replace( /\s/g, "") != '') ? $('#newMessage button[type=submit]').prop("disabled", false) :
																							$('#newMessage button[type=submit]').prop("disabled", true);
});

$(document).ready(function() {
	initMenu();
	initFtu();
	
	fph();
	$(window).resize(function() {
		fph();
	});
	
});