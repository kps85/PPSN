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
	
	$(".showRegister").click(function() {
		$("#register").fadeIn(tspeed);
	});
	
	$("#register input[type='reset']").click(function(e) {
		$("#register").fadeOut(tspeed);
		$("#register").find(".superDropdown").each(function() {
			$(this).find("p.id").text($(this).attr('default'));
		});		
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
	
	if ((window.location.href.split("/"))[4] == "profile" 
		 || (window.location.href.split("/"))[4] == "hashtag"
		 || (window.location.href.split("/"))[4] == "group") {
		var name = ((window.location.href.split("/"))[5]).split("?")[0];
		$(".ullink."+name).addClass("active");
	}
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
	var loginFilledCorrectly = $('#login input[type=text]').val() != '' && $('#login input[type=password]').val() != '';
	
	// console.log(loginFilledCorrectly);
	
	var registerFilledCorrectly = $('#name').val().replace(/\s/g, "") != '' 
	&& $('#email').val().replace( /\s/g, "") != '' &&
	$('#password').val().replace( /\s/g, "") != '' && $('#ack_password').val().replace( /\s/g, "") != '';
	
	(loginFilledCorrectly) ? $('#login input[type=submit]').prop("disabled", false) : $('#login input[type=submit]').prop("disabled", true);
	(registerFilledCorrectly) ? $('#register input[type=submit]').prop("disabled", false) : $('#register input[type=submit]').prop("disabled", true);	
}


function initInputValidation() {
	$(".checkNumeric").keypress(function(e) {
		// Erlaubt nur numerische Eingaben
		if( ( (e.keyCode < 48 || e.keyCode > 57) && e.keyCode != 8 ) || $(this).val().length > 5) {
			e.preventDefault();
			e.returnValue = false;
			return false;
		}
	});
	
	$(".faqContainer .post").click(function() {
		// Blendet Infotext ein und wechselt + zu - 
		var isActive = $(this).hasClass("active");
		
		// Alles zuruecksetzen
		$(".faqContainer").find(".active").removeClass("active");
		$(".faqContainer").find("p").addClass("hidden");
		$(".faqContainer").find(".glyphicon-minus").removeClass("glyphicon-minus").addClass("glyphicon-plus");
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

	$('#newMessage, #newComment').on("keyup", function(e) {
		// Ueberprueft ob Textfeld leer ist oder nur Leerzeichen enthaelt
		if($(this).find("textarea").val().replace( /\s/g, "") != '') {
			$(this).find('button[type=submit]').prop("disabled", false);
		} else {
			$(this).find('button[type=submit]').prop("disabled", true);
		}
	});	
}

function initInfoSettings() {
	// Wechselt die Info Navi und blendet relevante Formulare (Nachricht, Kontaktformular) ein.
	// Reagiert auf den hash in der aktiven URL	
	if ($('#body_info').length > 0 || $('#body_settings').length > 0) {
		($("#hash").length > 0) ? window.location.hash = $("#hash").attr("data-hint") : 
			(window.location.hash == '' && (window.location.href.split("/"))[5] == 'support') ? window.location.hash = 'nachricht' : '';
		
		infoChange((window.location.href.split("#"))[1]);
		
		$(window).on("hashchange", function() {
			infoChange((window.location.href.split("#"))[1]);
		});		
		
		$(".supportCont").each(function(index, element) {
      $(element).find('input[type=text]').keyup(function(e) {
				var mailRdy = $(element).find('input[type=text]').val().replace(/\s/g, "") != '' && 
											$(element).find('textarea').val().replace(/\s/g, "") != '';
        (mailRdy) ? $(element).find('button[type=submit]').prop("disabled", false) : 
										$(element).find('button[type=submit]').prop("disabled", true);
      });
      $(element).find('textarea').keyup(function(e) {
				var mailRdy = $(element).find('input[type=text]').val().replace(/\s/g, "") != '' && 
											$(element).find('textarea').val().replace(/\s/g, "") != '';
        (mailRdy) ? $(element).find('button[type=submit]').prop("disabled", false) : 
										$(element).find('button[type=submit]').prop("disabled", true);
      });
			$(element).find('button[type=reset]').click(function(e) {
        $(element).find('button[type=submit]').prop("disabled", true);
      });
    });
		
		$("#profBildUpdate").each(function(index, element) {
      var userImg = $(element).find("a").text().replace('"', '');
			if (userImg == 'picture/default.gif' || userImg == 'picture/gdefault.gif') {
				$(element).find("input[type=checkbox]").addClass("hidden");
				$(element).find("label").addClass("hidden");
			} else {
				$(element).find("label").html("&nbsp; Bild l&ouml;schen?");				
			}
    });
	}
}
function infoChange(hash) {		
	$('.ullink.active').removeClass('active');
	$('.'+hash).addClass('active');

	$(".supportCont").addClass('hidden');
	$("#"+hash).removeClass('hidden');
}

function initSearchResults() {
	if ($('.searchResultBox').length > 0) {
		showResults((window.location.href.split("#"))[1]);
		$(window).on("hashchange", function() {
			$(".searchResultButton.active").removeClass('active');
			$(".searchResultBox.active").removeClass('active');
			showResults((window.location.href.split("#"))[1]);
		});		
	}
}
function showResults(hash) {
	if (!hash) {
		var countUser = $(".searchResultButton.searchUser").attr("data-hint");
		var countGrp = $(".searchResultButton.searchGroup").attr("data-hint");
		var countHash = $(".searchResultButton.searchHash").attr("data-hint");
		var countMsg = $(".searchResultButton.searchMsg").attr("data-hint");
		hash = (countUser > 0) ? "searchUser" : (countGrp > 0) ? "searchGroup" : (countHash > 0) ? "searchHash" : (countMsg > 0) ? "searchMsg" : "";				
	}
	if (hash != '') {
		$('.'+hash).each(function(index, element) {
			$(element).addClass('active');
		});	
	}
}

function initVarious() {
	// Hide Info Button
	$(".hideInfo").click(function() {
		$(this).parent("div").hide();
	});
	$(".newMsg, .postToUser, .postToGroup").click(function(e) {
		var target = $(this).attr("data-hint");
		var symbol = ($(this).is(".postToUser")) ? "@" : "&";
		if ($(this).is(".postToUser") || $(this).is(".postToGroup")) {
			var val = $("#id_text").val().replace(symbol + target + " ", '');
			$("#id_text").val(symbol + target + " " + val);			
		}
    setTimeout(function() {
			$("#id_text").focus();
		}, 500);
  });
	$(".showMsgEdit, .showCmtEdit").click(function(e) {
		var mID = $(this).attr("data-hint");
		var tar = ($(this).is(".showMsgEdit")) ? "#postText"+mID : "#cmtText"+mID;
		var tarEdit = ($(this).is(".showMsgEdit")) ? "#postTextEdit"+mID : "#cmtTextEdit"+mID;
		$(this).addClass("hidden");		
    $(tar).addClass("hidden");
    $(tarEdit).removeClass("hidden");    
  });
	$(".hideMsgEdit, .hideCmtEdit").click(function(e) {
		var mID = $(this).attr("data-hint");
		var tar = ($(this).is(".hideMsgEdit")) ? "#postText"+mID : "#cmtText"+mID;
		var tarEdit = ($(this).is(".hideMsgEdit")) ? "#postTextEdit"+mID : "#cmtTextEdit"+mID;
		var tarBtn = ($(this).is(".hideMsgEdit")) ? ".showMsgEdit" : ".showCmtEdit";
		$(tarBtn).removeClass("hidden");
    $(tar).removeClass("hidden");
    $(tarEdit).addClass("hidden");
  });
  
  
  /* Super Dropdown List */
  $(".superDropdown").each(function() {
	  var $select = $(this);
	  $(this).hide();
	  var name = $(this).attr('placeholder');
	  var $div = $("<div>", {'class':'superDropdown'});
	  var $mainDiv = $("<div>", {'class':'superDropdownDiv'});
	  var $mainP = $("<p>", {'class':'id', 'text':name});
	  $(this).attr('default', name);
	  var $mainUl = $("<ul>", {'class':'superDropdownList'});
	  
	  var $content = $("<div>", {'class':'superDropdownContent'});
	  
	  $mainUl.hide();
	  $mainP.appendTo($div);
	  $content.appendTo($mainDiv);
	  $mainUl.appendTo($content);
	  $mainDiv.appendTo($div);
	  
	  
	  
	  $(this).children("optgroup").each(function() {
		  var $ul = $("<ul>", {'class':'superDropdownSub'});
		  var $p = $("<p>", {'class':'superSubOpener', 'text':$(this).attr('label')});
		  var $span = $("<span>", {'class':'superBack', 'html':'&larr; Zur&uuml;ck'});
		  
		  
		  
		  $span.click(function() {
			  $ul.fadeOut("slow");
		  	$content.animate({'left':'0'});
			$mainDiv.height("inherit");
		  });
		  
		  $ul.hide();
		  $p.click(function() {
			  
			  $(".superDropdownSub").hide();
			  
			  $mainDiv.height($ul.outerHeight(true));
			  $content.css({'left':'0'});
			  
			  $ul.show();
			  $content.animate({'left':'-100%'});

		  })
		  $(this).children("option").each(function() {
			var $li = $("<li>", {'text': $(this).val()});
			$li.click(function() {
				$select.val($(this).text());
				$mainUl.fadeOut(0);
				$mainP.text($(this).text());
				$content.animate({'left':'0'});
				$(".superDropdownSub").hide();
				$mainDiv.height("inherit");
				$mainP.addClass("active");
				$mainP.removeClass("opened");
				
			})
			$li.appendTo($ul);
		  });
		  
		  $span.appendTo($ul);
		  $p.appendTo($mainUl);
		$ul.appendTo($content);
	  })
	  $div.insertAfter($(this));
	  
	  $mainP.click(function() {
		  var width = $mainP.innerWidth() - 1;
			$mainDiv.width(width);
			$content.css({'left':'0'});
			$mainDiv.height("inherit");
		  $mainUl.fadeToggle(0);
		  $(this).toggleClass("opened");
	  });
	  
  });
	  
	$(".reply_link").click(function(e) {
    var data = $(this).attr("data-hint").split(" ");
	  $("#newCommentTitle").html("Antwort an " + data[1] + " verfassen"); 
	  $("#id_cmtToId").val(data[0]);  
  });
	
	$(".load_more").click(function(e) {
		var url = $(this).attr("data-hint");
		var last = $(".post").last().attr("data-hint");
		var user = $(".profilNick").attr("data-hint");
		var search_input = $(".load_more_search_input").attr("data-hint");
		var data = {
			user: user,
			last: last,
			search_input: search_input,
		}
		var getIt = function(url) {
			$.ajax({
				type:"GET",
				url: url,
				data: data,
				dataType: 'html',
				async: true,
				success: function(data) {
					switch(url.split("/")[2]) {
						case 'profile':
							$(".profileMessages").html(data);
							break;
						case 'hashtag':
							$("#searchMsg").html(data);
							break;
						case 'search':
							$("#searchMsg").html("<h4> Folgende Nachrichten wurden gefunden:</h4>" + data);
							break;
						default:
							$("#content").html(data);
					}
					if ($(".list_end").length > 0) {
						$(".load_more").hide();
					} else {
						$(".load_more").find("span").removeClass("glyphicon-time").addClass("glyphicon-refresh");
					}
				},
				error: function(xhr,err) {					
					alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
					alert("responseText: "+xhr.responseText);
				}
			});			
		};
		$(this).find("span").removeClass("glyphicon-refresh").addClass("glyphicon-time");
		getIt(url)
	});
  
	/* Smoothes Scrollen */
	$(function() {
	  $('a.scrollTop[href*=#]:not([href=#])').click(function() {
	    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {     
	        $('html,body').animate({
	          scrollTop: 0
	        }, 200);
	        return false;
	    }
	  });
	});
  
  
/* Scrollevent */
	$(window).scroll(function() {
		if($(window).scrollTop() > 0) {
			$(".newMsg").addClass("scrolled");
			$(".scrollTop").fadeIn("slow");
		} else {
			$(".newMsg").removeClass("scrolled");
			$(".scrollTop").fadeOut("slow");
		}
	});
  
}

$(document).ready(function() {
	initMenu();
	initList();
	initFtu();
	initInfoSettings();
	initSearchResults();
	initInputValidation();
	initVarious();
	
	fph();
	$(window).resize(function() {
		fph();
	});	
});