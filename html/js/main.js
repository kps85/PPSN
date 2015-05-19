$(document).ready(function() {
	for(var i = 0; i < 20; i++) {
		$(".post").first().clone().appendTo("#content");
	}
	
	var $menuOpener = $("<a>", {'class':'menuOpener'});
	$menuOpener.appendTo("header");
	
	$(".menuOpener").click(function() {
		var $a = $("aside");
		if($a.is(":hidden")) {
			$a.show();
			$a.animate({'left':0}, 300);
		} 
	});
	
	
	var $menuCloser = $("<a>", {'class':'menuCloser', 'html':'Zur&uuml;ck'});
	$menuCloser.appendTo("nav");
	
	$(".menuCloser").click(function() {
		var $a = $("aside");
		if($a.is(":visible")) {
			
			$a.animate({'left':'-100%'}, 300, function() {
				$a.hide();
			});
		} 
	});
	
	var windowWidth = $(window).width();
	var menuOpenerWasVisible = false;
	if($(".menuOpener").is(":visible")) {
		menuOpenerWasVisible = true;
	}
	
	$(window).resize(function() {
		if($(window).width() == windowWidth) return
		windowWidth = $(window).width();
		if($(".menuOpener").is(":hidden") && menuOpenerWasVisible) {
			$("aside").css({'left':'0'})
			$("aside").show();
			menuOpenerWasVisible = false;
		} else if($(".menuOpener").is(":visible") && !menuOpenerWasVisible) {
			$("aside").css({'left':'-100%'})
			$("aside").hide();
			menuOpenerWasVisible = true;
		}
	})
	
});