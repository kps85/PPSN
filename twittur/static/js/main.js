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

// API fuer Scrollbalken
var scrollApi = null;

// First Time Use
function initFtu() {
	if($("#ftu").length <= 0) return;	
	
	$(".showRegister").click(function() {
		$("#register").fadeIn(tspeed);
	});
	
	$("#register input[type='reset']").click(function(e) {
		$("#register").fadeOut(tspeed, function() {
			$(this).removeClass("active");
		});
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
	
	$menuOpener.prependTo("#head");
	
	$(".menuOpener, .menuOpener > *").click(function() {
		var $a = $("#aside");
		if($a.is(":hidden")) {
			$a.show();
			$a.animate({'left':0}, 300);
		} 
        if(scrollApi != null) {
            scrollApi.reinitialise();
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
    
	var $searchOpener = $("<a>", {'class':'searchOpener', 'href':'javascript:;', 'html':'<span class="glyphicon glyphicon-search"></span>'});
	$searchOpener.appendTo("#head");
	
	$searchOpener.click(function() {
		scrollToTop();
		$(".searchBar").slideToggle(300);
	})	
	
	var menuOpenerWasVisible = false;
	if($(".menuOpener").is(":visible")) {
		menuOpenerWasVisible = true;
	}
	
	var page = window.location.href.split("/")
	if ($.inArray(page[4], ["group", "hashtag", "profile"]) > -1) {
		var current = slug(decodeURI(page[5].split('?')[0]));
		switch (page[4]) {
			case 'group':
				$(".groups ."+current).addClass("active");
				break;
			case 'hashtag':
				$(".hashs ."+current).addClass("active");
				break;
			case 'profile':
				$(".following ."+current).addClass("active");
				break;
		}
	}
	
	$(window).resize(function() {
		if($(window).width() == windowWidth) return
		windowWidth = $(window).width();
		if($(".menuOpener").is(":hidden") && menuOpenerWasVisible) {
			$("#aside").css({'left':'0'});
			$("#aside").show();
			menuOpenerWasVisible = false;
		} else if($(".menuOpener").is(":visible") && !menuOpenerWasVisible) {
			$("#aside").css({'left':'-100%'})
			$("#aside").hide();
			menuOpenerWasVisible = true;
		}        
		if($(".searchOpener").is(":hidden")) {
				$(".searchBar").hide();
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
    
    
    // Huebsche Scrollbalken
    $('.scrollable').each(function() {
          $(this).jScrollPane({
              showArrows: $(this).is('.arrow')
          });
          scrollApi = $(this).data('jsp');
          var scrollTimeout;
          $(window).bind('resize',function() {
                  if (!scrollTimeout) {
                      scrollTimeout = setTimeout(function() {
                              scrollApi.reinitialise();
                              scrollTimeout = null;
                          }, 50);
                  }
              }
          );
      }
  );

}

// Notifications
var notificationShown = 7000; // Wie lange eine Notification angezeigt wird
var notificationPoll = 3000; // Wie oft auf neue Notifications geprüft werden soll

function showNotification($notify) {
	// Blendet eine einzelne Notification ein
    $(".liveNotifications").show();
	$notify.fadeIn(500);
	$notify.children(".notifyContent").animate({'left':'0'},500);
}

function deleteNotification($notify, timer) {
	// Timer clearen
	clearTimeout(timer);
	// So ausblenden, dass die anderen Notifications nicht ruckeln
	var height = $notify.outerHeight(true);
	var margin = 10;
	$notify.fadeTo(300, 0.01).animate({marginTop: -height + margin, left:'-100%'}, 500, function() {
		$(this).remove();
        if($(".liveNotifications .notify").length <= 0) {
            $(".liveNotifications").hide();
        }
	});
}


function notify(content, link) {
	// Template holen (s. template/layout/notificationBox.html)
	var $template = $(".notify.template");
	var $new = $template.clone().removeClass("template");
	// Funktion zum loeschen der Notification
	var timer = null;
	var fnDelete = function() {
		deleteNotification($new, timer);
	}
	// Automatisch loeschen
	timer = setTimeout(fnDelete, notificationShown);
	// Oder durch Klick
	$new.find(".notifyClose").click(fnDelete);
	// Beim Hover wird der Timer kurz gestoppt
	$new.hover(function() {
		clearTimeout(timer);
	}, function() {
		timer = setTimeout(fnDelete, notificationShown);
	});
	
	// Text einfuegen
	var $message = $new.find(".notifyMessage");
	$message.html(content);
	// Link einfuegen
	if(link != null) {
		$message.attr('href',link);
		$message.addClass("hover");
	}	
	
	// In die Notificationleiste einfuegen
	$new.prependTo(".liveNotifications");
	
	// Anzeigen!
	showNotification($new);
	return $new;
}

function notificationTest(message, delay) {
	// Methode zum Testen der Notifications - message wird nach delay (ms) eingeblendet
	setTimeout(function() {
		notify(message);
	}, delay);
}

function getNotifications(user, verify, url) {
    $.post( url, {'user': user, 'hash': verify}, function(data) {
        if(data != "") {
            var $xml = $(data);
            $xml.find("notification").each(function() {
                // unused:  var date = $(this).attr("date");
                var link = $(this).attr("link");
                var text = $(this).text();
                notify(text, link);   
            });
        }
    });
}

function initNotifications() {
	if(!$(".liveNotifications").length) return;
	
	var user = $("body").attr('data-user');
	var verify = $("body").attr('data-verify');
	var url = $('link[rel="api"]').attr('href');
	if(user == "" || verify == "") return;
	setInterval(function() {
			getNotifications(user, verify, url);
	}, notificationPoll);
    
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

	function check_input(e) {
		// Ueberprueft ob Textfeld leer ist oder nur Leerzeichen enthaelt
		if($(e).find("textarea").val().replace( /\s/g, "") != '') {
			$(e).find('button[type=submit]').prop("disabled", false);
		} else {
			$(e).find('button[type=submit]').prop("disabled", true);
		}
	}

	$('#newMessage').on("keyup", function(e) { check_input(this); });
	$('div.newComment').each(function(index, element) {
    $(element).on("keyup", function(e) { check_input(this); });
  });
	
	$(".newMsgPctr span").click(function(e) {
		$(".newMsgPctr .glyphicon").toggleClass("glyphicon-plus glyphicon-minus");
		$(".newMsgPctr div").toggleClass("hidden");
  });	
		
	$(".newMsgPctr input[type=file]").change(function(e) {
		var html = ""
		var path = URL.createObjectURL(e.target.files[0]);
		if (checkImage(this)) {
			$(this).val("");
			html = "<div class='img_prev text-center'><font color='#ff0000'>Nur Bilddateien erlaubt!</font></div>";
		} else {
			html = "<div class='img_prev text-center'><img class='img-thumbnail' src='"+path+"' width='200'></div>";
		}
		$(".newMsgPctr div").find(".img_prev").remove();
		$(".newMsgPctr div").prepend(html);
	});
}
	
function checkImage(element) {
	var error = false
	var val = $(element).val();
	switch(val.substring(val.lastIndexOf('.') + 1).toLowerCase()) {
		case 'gif': case 'jpg': case 'png': case 'jpeg':
			break;
		default:
			error = true
			break;
	}
	return error
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
		
		$("#profBildUpdate input[type=file]").change(function(e) {
			var html = ""
			var path = URL.createObjectURL(e.target.files[0]);
			var help_text = ((window.location.href.split("/"))[4] == 'settings') ? 
													"Dieses Bild wird auf Deinem Profil (gro&szlig;) und in deinen Nachrichten (klein) angezeigt." :
													"Dieses Bild wird auf der Gruppenseite zu sehen sein!";
			if (checkImage(this)) {
				$(this).val("");
				help_text += "<div class='img_prev text-center'><font color='#ff0000'>Nur Bilddateien erlaubt!</font></div>";				
			} else {
				help_text += "<br><strong>Achtung!</strong> Dies ist nur eine Vorschau.<br>" + 
										 "Die &Auml;nderung wird erst beim Speichern des Formulars &uuml;bernommen."
				$(".profilePictures img").each(function(index, element) {
					$(element).attr("src", path);
				});				
			}
			$(".profilePictures").find(".help-block").html(help_text);
			
    });
		
		$(".memberHead").click(function(e) {
      $(".memberList").toggleClass("hidden");
      $(this).find("span").toggleClass("glyphicon-minus glyphicon-plus");
    });
		
		if ($("#id_category").val() == "Kategorie erstellen" || $("#id_category").val() == "anderes Thema") $("#id_other").removeClass("hidden");
		$("#id_category").on('change', function(e) {
      if ($(this).val() == 'Kategorie erstellen' || $(this).val() == 'anderes Thema') {
				$("#id_other").removeClass('hidden');
			} else {
				if (!$("#id_other").is("hidden")) $("#id_other").addClass("hidden");
				$("#id_other").val("");
			}
    });
		
		/* gets a new verifyHash for user and returns value to user_data_form */
		$("#id_refresh_hash").click(function(e) {
			var info = {
				url: $(this).attr("data-hint")
			}
			$.ajax({
				type:"GET",
				url: info.url,
				data: null,
				dataType: 'html',
				async: true,
				success: function(data) {
					$("#id_verifyHash").val(data);
				},
				error: function(xhr,err) {					
					alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
					alert("responseText: "+xhr.responseText);
				}
			});			      
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
  
  /* Super Dropdown List */
  $(".superDropdown").each(function() {
	  var $select = $(this);
	  $(this).hide();
	  var name = $(this).attr('placeholder');
	  var $div = $("<div>", {'class':'superDropdown'});
	  var $mainDiv = $("<div>", {'class':'superDropdownDiv'});
	  var $mainP = $("<p>", {'class':'id', 'html':name+'<span class="glyphicon glyphicon-chevron-down pull-right"></span>'});
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
					$mainP.html($(this).text()+'<span class="glyphicon glyphicon-chevron-down pull-right"></span>');
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
	  });     
      
		$(this).children("option").each(function() {
			var $li = $("<li>", {'class':'superSubOpener', 'text':$(this).text()});
			var optionVal = $(this).val()
			$li.click(function() {
				$select.val(optionVal);
				console.log($select.val() + " gewaehlt");
				$mainUl.fadeOut(0);
				$mainP.html($(this).text()+'<span class="glyphicon glyphicon-chevron-down pull-right"></span>');
				$(".superDropdownSub").hide();
				$mainP.addClass("active");
				$mainP.removeClass("opened");
			})
			$li.appendTo($mainUl);
		})
      
	  $div.insertAfter($(this));
	  
	  $mainP.click(function() {
		  var width = $mainP.innerWidth();
			$mainDiv.width(width);
			$content.css({'left':'0'});
			$mainDiv.height("inherit");
		  $mainUl.fadeToggle(0);
		  $(this).toggleClass("opened");
	  });	  
  });  
	
	/* Smoothes Scrollen */
	$(function() {
	  $('a.scrollTop[href*=#]:not([href=#])').click(function() {
	    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {     
				scrollToTop();
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


function msgManagement() {
	$(".newMsg, .postToUser, .postToGroup").unbind("click").click(function(e) {
		var target = $(this).attr("data-hint");
		var symbol = ($(this).is(".postToUser")) ? "@" : "&";
		if ($(this).is(".postToUser") || $(this).is(".postToGroup")) {	
			if ($(this).is(".postToGroup")) {
				$("#newMessage select.superDropdown").val(symbol+target);
				$("#newMessage").find("div.superDropdown > p").html(symbol+target+'<span class="glyphicon glyphicon-chevron-down pull-right"></span>');
			} else {
				var val = $("#id_text").val().replace(symbol + target + " ", '');
				$("#newMessage").find("textarea").val(symbol + target + " " + val);	
			}
		}
    setTimeout(function() {
			$("#newMessage").find("textarea").focus();
		}, 500);
  });
	$(".showMsgEdit, .showCmtEdit, .hideMsgEdit, .hideCmtEdit").unbind("click").click(function(e) {
		var id = $(this).attr("data-hint");
		var togElements = ".showMsgEdit."+id+", .showCmtEdit."+id+", .postText."+id+", .postTextEdit."+id+", .cmtText."+id+", .cmtTextEdit."+id;
		$(togElements).toggleClass("hidden");
  });  
	  
	$(".reply_link").unbind("click").click(function(e) {
    var data = $(this).attr("data-hint").split(" ");
	  $("#newComment"+data[0]).find(".modal-title").html("Antwort an " + data[1] + " verfassen");
  });
	
	$(".ignoreCmtButton, .ignoreMsgButton, .deleteMsgButton, .saveMsgEdit, .saveCmtEdit, .favoMsg").unbind("click").click(function(e) {
		var hint = $(this).attr("data-hint").split(" ");
    var info = {
			what: hint[0],
			id: hint[1],
			user: hint[2],
			url: hint[3]
		}
		if ($(this).is(".saveMsgEdit")) {
			info.clear = $(".postTextEdit."+info.id).find("input[type=checkbox]").prop('checked');
			info.safety = $(".postTextEdit."+info.id).find("select.superDropdown").val();
			info.val = $(".postTextEdit."+info.id).find("textarea").val();
		} else if ($(this).is(".saveCmtEdit")) {
			info.val = $(".cmtTextEdit."+info.id).find("textarea").val();			
		}
		var hideIt = function() {
			$.ajax({
				type:"GET",
				url: info.url,
				data: info,
				dataType: 'html',
				async: true,
				success: function(data) {
					switch(info.what) {
						case 'hide_msg':
							if (data.search('warning') > 0) {
								$("#post"+info.id).find(".postHide").html(data);
							} else {
								$("#post"+info.id).each(function(index, element) {
									$(element).toggleClass("postIgnore");
									$(element).find(".icon, .postMeta, .postText, .postReply, .postHide").toggleClass("hidden");
									$(element).find(".postContent").toggleClass("isHidden");
									$(element).find(".ignoreMsgButton").toggleClass("glyphicon-eye-open glyphicon-eye-close");
									$(element).find(".postHide").html(data);
								});
							}
							break;
						case 'hide_cmt':	
							if (data.search('warning') > 0) {
								$("#cmt"+info.id).find(".postHide").html(data);
							} else {	
								$("#cmt"+info.id).each(function(index, element) {
									var hideElements = ".cmtMeta."+info.id+", .cmtText."+info.id+", .reply_link."+info.id+", .postHide."+info.id;
									$(element).find(hideElements).toggleClass("hidden");
									$(element).find(".ignoreCmtButton."+info.id).toggleClass("glyphicon-eye-open glyphicon-eye-close");
									$(element).find(".postHide."+info.id).html(data);
								});
							}
							break;
						case 'del_msg':
							$("#post"+info.id).each(function(index, element) {
								$("#delMsg"+info.id+"Modal").modal('hide');
								$(element).toggleClass("postIgnore");
								var delElements = ".icon, .postMeta, .postText, .postTextEdit, .postReply, .postEdit";
								$(element).find(delElements).remove();
								$("#newComment"+info.id).remove();
								$(element).find(".postContent").toggleClass("isHidden");
								$(element).find(".postHide").toggleClass("hidden").html(data);
								setTimeout(function() {
									$("#delMsg"+info.id+"Modal").remove();
								}, 1000);
							});
							break;
						case 'del_cmt':
							$("#cmt"+info.id).each(function(index, element) {
								$("#delCmt"+info.id+"Modal").modal('hide');
								var remElements = ".cmtMeta."+info.id+", .cmtText."+info.id+", .reply_link."+info.id+", .cmtEdit."+info.id;
								$(element).find(remElements).remove();
								$("#newComment"+info.id).remove();
								$(element).find(".postHide."+info.id).toggleClass("hidden").html(data);
								setTimeout(function() { $("#delCmt"+info.id+"Modal").remove(); }, 1000);
							});
							break;
						case 'upd_msg':
							var togElements = ".showMsgEdit."+info.id+", .showCmtEdit."+info.id+", .postText."+info.id+", .postTextEdit."+info.id+", .cmtText."+info.id+", .cmtTextEdit."+info.id;
							$(togElements).toggleClass("hidden");
							if ($(".postTextEdit."+info.id).length > 0) {
								$(".postText."+info.id).find("p").html(data);
								$(".delMsg"+info.id+"Modal").find(".modal-body").html("<em>"+data+"</em>");
							} else {
								$(".cmtText."+info.id).find("p").html(data);
								$(".delCmt"+info.id+"Modal").find(".modal-body").html("<em>"+data+"</em>");
							}
							if (info.clear) $("#post"+info.id).find(".msgPctr, .msgPctrEdit, .msgPctrModal").remove();
							break;
					}
				},
				error: function(xhr,err) {					
					alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
					alert("responseText: "+xhr.responseText);
				}
			});			
		};
		hideIt();
  });
}


function loadMore() {	
	if ($("#body_index").length > 0 || $("#body_profile").length > 0 || $("#body_group").length > 0 || 
			$("#body_hashtag").length > 0 || $("#body_search").length > 0) {
		$(".load_more").click(function(e) {
			var url = $(this).attr("data-hint");
			var info = {
				page: $(this).attr("data-page"),
				user: $(this).attr("data-user"),
				group: $(this).attr("data-group"),
				search_input: $(this).attr("data-search"),
				hash: $(this).attr("data-hash"),
				length: $(this).attr("data-length"),
				post: $(".post").last().attr("data-hint")
			}
			//alert(info.post)
			var getIt = function(url) {
				$.ajax({
					type:"GET",
					url: url,
					data: info,
					dataType: 'html',
					async: true,
					success: function(data) {
						setIt(data, info.page);
					},
					error: function(xhr,err) {					
						alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
						alert("responseText: "+xhr.responseText);
					}
				});			
			};
			var setIt = function(data, page) {
				switch(page) {
					case 'profile':
						$(".profileMessages").append(data);
						break;
					case 'group':
						$(".profileMessages").append(data);
						break;
					case 'hashtag':
						$("#searchMsg").append(data);
						break;
					case 'search':
						$("#searchMsg").append(data);
						break;
					default:
						$("#content").append(data);
				}
				if ($(".list_end").length > 0) {
					$(".load_more").hide();
				} else {
					$(".load_more").find("span").toggleClass("glyphicon-refresh glyphicon-time");
					$(".load_more").attr("data-length", $(".post").length);
				}
				msgManagement();
			}
			$(this).find("span").toggleClass("glyphicon-refresh glyphicon-time");
			getIt(url)
		});
	} else if ($(".notification.panel").length > 0) {
		var count = 4;
		var setNtfcLength = function(more) {
			if (more) count += 5;
			$(".notification.panel").each(function(index, element) {
				if (index <= count) $(element).removeClass("hidden");
			});
			($(".notification.panel").length > count) ? $(".load_more").removeClass("hidden") : $(".load_more").addClass("hidden");
		}
		$(".load_more").click(function(e) {
			var gIcon = $(this).find("span");
			gIcon.toggleClass("glyphicon-refresh glyphicon-time");
      setNtfcLength(true);
			gIcon.toggleClass("glyphicon-refresh glyphicon-time");
    });
		setNtfcLength();
	}
}


/* Nach oben scrollen */
function scrollToTop() {
	$('html,body').animate({
		scrollTop: 0
	}, 200);
}

/* slugify string snippet found on http://stackoverflow.com/questions/1053902/how-to-convert-a-title-to-a-url-slug-in-jquery */
var slug = function(str) {
  str = str.replace(/^\s+|\s+$/g, ''); // trim
  str = str.toLowerCase();

  // remove accents, swap ñ for n, etc
  var from = "ãàáäâẽèéëêìíïîõòóöôùúüûñç·/_,:;";
  var to   = "aaaaaeeeeeiiiiooooouuuunc------";
  for (var i=0, l=from.length ; i<l ; i++) {
    str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
  }

  str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
    .replace(/\s+/g, '-') // collapse whitespace and replace by -
    .replace(/-+/g, '-'); // collapse dashes

  return str;
};


$(document).ready(function() {
	initMenu();
	initList();
	initFtu();
  initNotifications();
	initInfoSettings();
	initSearchResults();
	initInputValidation();
	initVarious();
	msgManagement();
	loadMore();
	
	fph();
	$(window).resize(function() {
		fph();
	});	
});