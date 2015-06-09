// Fullpage Height

function fph() { 
	// Hax
	var $as = $("#aside");
	if(!$as.length) {
		$as = $("<div>", {'id':'aside'});
		$as.prependTo("body");
	} 
    var vph = $(window).height();
	// Elemente, die immer die volle Hoehe haben sollen
    $('.full-page').css({'minHeight':vph + "px"});
	
	// Elemente, die nur auf Desktops die voelle Hoehe haben sollen :)
	if($as.is(":visible")) {
		$(".full-page-nomobile").css({'minHeight':vph + "px"});
	} else {
		$(".full-page-nomobile").css({'minHeight':'inherit'});
	}
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
	
	
	$(".showRegister").click(function() {
		$("#register").fadeIn(tspeed);
	});
	
	$("#register input[type='reset']").click(function() {
		$(".active").removeClass("active");
		$("#register").fadeOut(tspeed);
		
		
	})
	
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

function initList() {
	
	// Hauptfenster nicht mitscrollen
	$('#list, .scrollfix').bind('mousewheel DOMMouseScroll', function(e) {
	    var scrollTo = null;

	    if (e.type == 'mousewheel') {
	        scrollTo = (e.originalEvent.wheelDelta * -1);
	    }
	    else if (e.type == 'DOMMouseScroll') {
	        scrollTo = 40 * e.originalEvent.detail;
	    }

	    if (scrollTo) {
	        e.preventDefault();
	        $(this).scrollTop(scrollTo + $(this).scrollTop());
	    }
	});
}

function validateFtu() {
	// Validiert die Daten der Login/Registrierungsseite
	// TODO: Einfacher gestalten...	
	// das .replace hier war überflüssig. Wenn autofill, dann nur mit validen Daten. valide Daten = Passwort ohne Leerzeichen.
	var loginFilledCorrectly = $('#login input[type=text]').val() != '' 
	&& $('#login input[type=password]').val() != '';
	
	// console.log(loginFilledCorrectly);
	
	var registerFilledCorrectly = $('#name').val().replace(/\s/g, "") != '' 
	&& $('#email').val().replace( /\s/g, "") != '' &&
	$('#password').val().replace( /\s/g, "") != '' && $('#ack_password').val().replace( /\s/g, "") != '' &&
	$('#academicDiscipline').val().replace( /\s/g, "") != '';
	
	(loginFilledCorrectly) ? $('#login input[type=submit]').prop("disabled", false) : $('#login input[type=submit]').prop("disabled", true);
	(registerFilledCorrectly) ? $('#register input[type=submit]').prop("disabled", false) : $('#register input[type=submit]').prop("disabled", true);	
}


function initInputValidation() {
	$(".checkNumeric").keypress(function(e) {
		// Erlaubt nur numerische Eingaben
		if((e.keyCode < 48 || e.keyCode > 57) && e.keyCode != 8) {
			e.preventDefault();
			 e.returnValue = false;
			return false;
		}
	});
	
	$(".faqContainer .post").click(function() {
		// Blendet Infotext ein und wechselt + zu - 
		var isActive = $(this).hasClass("active");
		$(this).toggleClass("active", !isActive);
		$(this).find("p").toggleClass("hidden", isActive);
		$(this).find("h4 span").toggleClass('glyphicon-minus', !isActive).toggleClass('glyphicon-plus', isActive);
	})


	if($("#ftu, #register").length) {
		validateFtu();
	}
	$("#ftu input, #register input").on("keyup", function() {
		validateFtu();
	});

	$('#newMessage').on("keyup", function(e) {
		// Ueberprueft ob Textfeld leer ist oder nur Leerzeichen enthaelt
		if($(this).find("textarea").val().replace( /\s/g, "") != '') {
			$('#newMessage button[type=submit]').prop("disabled", false);
		} else {
			$('#newMessage button[type=submit]').prop("disabled", true);
		}
	});
	
}


function initInfoSettings() {
	// Wechselt die Info Navi und blendet relevante Formulare (Nachricht, Kontaktformular) ein.
	// Reagiert auf den hash in der aktiven URL	
	if ($('#body_info').length > 0 || $('#body_settings').length > 0) {
		
		infoChange((window.location.href.split("#"))[1]);
		
		$(window).on("hashchange", function() {
			infoChange((window.location.href.split("#"))[1]);
		});
		
	}
}

function infoChange(hash) {		
	$('.ullink.active').removeClass('active');
	$('.'+hash).addClass('active');

	$(".supportCont").addClass('hidden');
	$("#"+hash).removeClass('hidden');
}


function initVarious() {
	// Hide Info Button
	$(".hideInfo").click(function() {
		$(this).parent("div").hide();
	});
	$(".newMsg").click(function(e) {
    setTimeout(function() {
			$("#id_text").focus();
		}, 500);
  });
	$(".showMsgEdit").click(function(e) {
		var mID = $(this).attr("data-hint");
		$(this).addClass("hidden");
    $("#postText"+mID).addClass("hidden");
    $("#postTextEdit"+mID).removeClass("hidden");    
  });
	$(".hideMsgEdit").click(function(e) {
		var mID = $(this).attr("data-hint");
		$(".showMsgEdit").removeClass("hidden");
    $("#postText"+mID).removeClass("hidden");
    $("#postTextEdit"+mID).addClass("hidden");
  });
  
  $(".superDropdown").each(function() {
	  var $select = $(this);
	  $(this).hide();
	  var name = $(this).attr('placeholder');
	  var $div = $("<div>", {'class':'superDropdown'});
	  var $mainP = $("<p>", {'text':name});
	  var $mainUl = $("<ul>", {'class':'superDropdownList'});
	  $mainUl.hide();
	  $mainP.appendTo($div);
	  $mainUl.appendTo($div);
	  
	  $(this).children("optgroup").each(function() {
		  var $ul = $("<ul>", {'class':'superDropdownSub'});
		  var $p = $("<p>", {'class':'superSubOpener', 'text':$(this).attr('label')});
		  
		  $ul.hide();
		  $p.click(function() {
			  
			  var visible = $ul.is(":visible");
			  $(".superDropdownSub").hide();
			  if(!visible) {
				  $ul.toggle();
			  }
		  })
		  $(this).children("option").each(function() {
			var $li = $("<li>", {'text': $(this).val()});
			$li.click(function() {
				$select.val($(this).text());
				$mainUl.fadeOut(0);
				$mainP.text($(this).text());
				$mainP.addClass("active");
				$mainP.removeClass("opened");
			})
			$li.appendTo($ul);
		  });
		  $p.appendTo($mainUl);
		$ul.appendTo($mainUl);
	  })
	  $div.insertAfter($(this));
	  
	  $mainP.click(function() {
		  var width = $mainP.innerWidth() - 1;
			$mainUl.width(width);
		  $mainUl.fadeToggle(0);
		  $(this).toggleClass("opened");
	  })
	  
  });
  
}

$(document).ready(function() {
	initMenu();
	initList();
	initFtu();
	initInfoSettings();
	initInputValidation();
	initVarious();
	
	fph();
	$(window).resize(function() {
		fph();
	});	
});