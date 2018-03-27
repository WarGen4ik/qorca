jQuery(function ($) {

    var BRUSHED = window.BRUSHED || {};

    /* ==================================================
     Mobile Navigation
     ================================================== */
    var mobileMenuClone = $('#menu').clone().attr('id', 'navigation-mobile');

    BRUSHED.mobileNav = function () {
        var windowWidth = $(window).width();

        if (windowWidth <= 979) {
            if ($('#mobile-nav').length > 0) {
                mobileMenuClone.insertAfter('#menu');
                $('#navigation-mobile #menu-nav').attr('id', 'menu-nav-mobile');
            }
        } else {
            $('#navigation-mobile').css('display', 'none');
            if ($('#mobile-nav').hasClass('open')) {
                $('#mobile-nav').removeClass('open');
            }
        }
    };

    BRUSHED.listenerMenu = function () {
        $('#mobile-nav').on('click', function (e) {
            $(this).toggleClass('open');

            if ($('#mobile-nav').hasClass('open')) {
                $('#navigation-mobile').slideDown(500, 'easeOutExpo');
            } else {
                $('#navigation-mobile').slideUp(500, 'easeOutExpo');
            }
            e.preventDefault();
        });

        $('#menu-nav-mobile a').on('click', function () {
            $('#mobile-nav').removeClass('open');
            $('#navigation-mobile').slideUp(350, 'easeOutExpo');
        });
    };


    /* ==================================================
     Slider Options
     ================================================== */

    BRUSHED.slider = function () {
        $.supersized({
            // Functionality
            slideshow: 1,			// Slideshow on/off
            autoplay: 1,			// Slideshow starts playing automatically
            start_slide: 1,			// Start slide (0 is random)
            stop_loop: 0,			// Pauses slideshow on last slide
            random: 0,			// Randomize slide order (Ignores start slide)
            slide_interval: 12000,		// Length between transitions
            transition: 1, 			// 0-None, 1-Fade, 2-Slide Top, 3-Slide Right, 4-Slide Bottom, 5-Slide Left, 6-Carousel Right, 7-Carousel Left
            transition_speed: 300,		// Speed of transition
            new_window: 1,			// Image links open in new window/tab
            pause_hover: 0,			// Pause slideshow on hover
            keyboard_nav: 1,			// Keyboard navigation on/off
            performance: 1,			// 0-Normal, 1-Hybrid speed/quality, 2-Optimizes image quality, 3-Optimizes transition speed // (Only works for Firefox/IE, not Webkit)
            image_protect: 1,			// Disables image dragging and right click with Javascript

            // Size & Position
            min_width: 0,			// Min width allowed (in pixels)
            min_height: 0,			// Min height allowed (in pixels)
            vertical_center: 1,			// Vertically center background
            horizontal_center: 1,			// Horizontally center background
            fit_always: 0,			// Image will never exceed browser width or height (Ignores min. dimensions)
            fit_portrait: 1,			// Portrait images will not exceed browser height
            fit_landscape: 0,			// Landscape images will not exceed browser width

            // Components
            slide_links: 'blank',	// Individual links for each slide (Options: false, 'num', 'name', 'blank')
            thumb_links: 0,			// Individual thumb links for each slide
            thumbnail_navigation: 0,			// Thumbnail navigation
            slides: [			// Slideshow Images
                {
                    image: slider_items_location + 'image01.jpg',
                    title: '<div class="slide-content">Q-Orca</div>',
                    thumb: '',
                    url: ''
                },
                {
                    image: slider_items_location + 'image02.jpg',
                    title: '<div class="slide-content">Q-Orca</div>',
                    thumb: '',
                    url: ''
                },
                {
                    image: slider_items_location + 'image03.jpg',
                    title: '<div class="slide-content">Q-Orca</div>',
                    thumb: '',
                    url: ''
                },
                {
                    image: slider_items_location + 'image04.jpg',
                    title: '<div class="slide-content">Q-Orca</div>',
                    thumb: '',
                    url: ''
                }
            ],

            // Theme Options
            progress_bar: 0,			// Timer for each slide
            mouse_scrub: 0

        });

    };


    /* ==================================================
     Navigation Fix
     ================================================== */

    BRUSHED.nav = function () {
        $('.sticky-nav').waypoint('sticky');
    };


    /* ==================================================
     Filter Works
     ================================================== */

    BRUSHED.filter = function () {
        if ($('#projects').length > 0) {
            var $container = $('#projects');

            $container.imagesLoaded(function () {
                $container.isotope({
                    // options
                    animationEngine: 'best-available',
                    itemSelector: '.item-thumbs',
                    layoutMode: 'fitRows'
                });
            });


            // filter items when filter link is clicked
            var $optionSets = $('#options .option-set'),
                $optionLinks = $optionSets.find('a');

            $optionLinks.click(function () {
                var $this = $(this);
                // don't proceed if already selected
                if ($this.hasClass('selected')) {
                    return false;
                }

                var $optionSet = $this.parents('.option-set');
                $optionSet.find('.selected').removeClass('selected');
                $this.addClass('selected');

                // make option object dynamically, i.e. { filter: '.my-filter-class' }
                var options = {},
                    key = $optionSet.attr('data-option-key'),
                    value = $this.attr('data-option-value');
                // parse 'false' as false boolean
                value = value === 'false' ? false : value;
                options[key] = value;
                if (key === 'layoutMode' && typeof changeLayoutMode === 'function') {
                    // changes in layout modes need extra logic
                    changeLayoutMode($this, options)
                } else {
                    // otherwise, apply new options
                    $container.isotope(options);
                    var projects = $('#thumbs');
                    // if (projects.length == 1) {
                    //     var node = document.createElement("LI");
                    //     node.className += 'item-thumbs span3 no-competitions';
                    //     var textnode = document.createTextNode("Water");
                    //     node.appendChild(textnode);
                    //     projects.append(node);
                    // }
                }

                return false;
            });
        }
    };


    /* ==================================================
     FancyBox
     ================================================== */

    BRUSHED.fancyBox = function () {
        if ($('.fancybox').length > 0 || $('.fancybox-media').length > 0 || $('.fancybox-various').length > 0) {

            $(".fancybox").fancybox({
                padding: 0,
                beforeShow: function () {
                    this.title = $(this.element).attr('title');
                    this.title = '<h4>' + this.title + '</h4>' + '<p>' + $(this.element).parent().find('img').attr('alt') + '</p>';
                },
                helpers: {
                    title: {type: 'inside'},
                }
            });

            $('.fancybox-media').fancybox({
                openEffect: 'none',
                closeEffect: 'none',
                helpers: {
                    media: {}
                }
            });
        }
    };
//---------------------

//---------------------
    var is_sent = false;
    $('.overlay-img, .overlay-text-thumb').click(function () {
        $('.avatar-input').click();

        if (!is_sent) {
            is_sent = true;
            $(".avatar-input").change(function () {
                var $input = $(".avatar-input");
                var fd = new FormData;

                fd.append('img', $input.prop('files')[0]);

                $.ajax({
                    url: '/auth/profile',
                    data: fd,
                    processData: false,
                    contentType: false,
                    type: 'POST',
                    success: function () {
                        $('.avatar-input').clearData();
                    },
                    beforeSend: function (xhr, settings) {
                        function getCookie(name) {
                            var cookieValue = null;
                            if (document.cookie && document.cookie != '') {
                                var cookies = document.cookie.split(';');
                                for (var i = 0; i < cookies.length; i++) {
                                    var cookie = jQuery.trim(cookies[i]);
                                    // Does this cookie string begin with the name we want?
                                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                        break;
                                    }
                                }
                            }
                            return cookieValue;
                        }

                        if (!(/^http:.*!/.test(settings.url) || /^https:.*/.test(settings.url))) {
                            // Only send the token to relative URLs i.e. locally.
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });
                setTimeout(function () {

                    location.reload();
                }, 1000);
            });

        }
    });


    /* ==================================================
     Contact Form
     ================================================== */

    BRUSHED.contactForm = function () {
        $("#contact-submit").on('click', function () {
            $contact_form = $('#contact-form');

            var fields = $contact_form.serialize();

            $.ajax({
                type: "POST",
                url: "/staticfiles/php/contact.php",
                data: fields,
                dataType: 'json',
                success: function (response) {

                    if (response.status) {
                        $('#contact-form input').val('');
                        $('#contact-form textarea').val('');
                    }

                    $('#response').empty().html(response.html);
                }
            });
            return false;
        });
    };


    /* ==================================================
     Twitter Feed
     ================================================== */

    BRUSHED.tweetFeed = function () {

        var valueTop = -64; // Margin Top Value

        $("#ticker").tweet({
            modpath: '/staticfiles/js/twitter/',
            username: "Bluxart", // Change this with YOUR ID
            page: 1,
            avatar_size: 0,
            count: 10,
            template: "{text}{time}",
            filter: function (t) {
                return !/^@\w+/.test(t.tweet_raw_text);
            },
            loading_text: "loading ..."
        }).bind("loaded", function () {
            var ul = $(this).find(".tweet_list");
            var ticker = function () {
                setTimeout(function () {
                    ul.find('li:first').animate({marginTop: valueTop + 'px'}, 500, 'linear', function () {
                        $(this).detach().appendTo(ul).removeAttr('style');
                    });
                    ticker();
                }, 5000);
            };
            ticker();
        });

    };


    /* ==================================================
     Menu Highlight
     ================================================== */

    BRUSHED.menu = function () {
        $('#menu-nav, #menu-nav-mobile').onePageNav({
            currentClass: 'current',
            changeHash: true,
            scrollSpeed: 700,
            scrollOffset: 30,
            scrollThreshold: 0.5,
            easing: 'easeOutExpo',
            filter: ':not(.external)'
        });
    };


    /* ==================================================
     Next Section
     ================================================== */

    BRUSHED.goSection = function () {
        $('#nextsection').on('click', function () {
            $target = $($(this).attr('href')).offset().top - 30;

            $('body, html').animate({scrollTop: $target}, 750, 'easeOutExpo');
            return false;
        });
    };

    /* ==================================================
     GoUp
     ================================================== */

    BRUSHED.goUp = function () {
        $('#goUp').on('click', function () {
            $target = $($(this).attr('href')).offset().top - 30;

            $('body, html').animate({scrollTop: $target}, 750, 'easeOutExpo');
            return false;
        });
    };


    /* ==================================================
     Scroll to Top
     ================================================== */

    BRUSHED.scrollToTop = function () {
        var windowWidth = $(window).width(),
            didScroll = false;

        var $arrow = $('#back-to-top');

        $arrow.click(function (e) {
            $('body,html').animate({scrollTop: "0"}, 750, 'easeOutExpo');
            e.preventDefault();
        });

        $(window).scroll(function () {
            didScroll = true;
        });

        setInterval(function () {
            if (didScroll) {
                didScroll = false;

                if ($(window).scrollTop() > 1000) {
                    $arrow.css('display', 'block');
                } else {
                    $arrow.css('display', 'none');
                }
            }
        }, 250);
    };

    /* ==================================================
     Thumbs / Social Effects
     ================================================== */

    BRUSHED.utils = function () {

        $('.item-thumbs').bind('touchstart', function () {
            $(".active").removeClass("active");
            $(this).addClass('active');
        });

        $('.image-wrap').bind('touchstart', function () {
            $(".active").removeClass("active");
            $(this).addClass('active');
        });

        $('#social ul li').bind('touchstart', function () {
            $(".active").removeClass("active");
            $(this).addClass('active');
        });

    };

    /* ==================================================
     Accordion
     ================================================== */

    BRUSHED.accordion = function () {
        var accordion_trigger = $('.accordion-heading.accordionize');

        accordion_trigger.delegate('.accordion-toggle', 'click', function (event) {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
                $(this).addClass('inactive');
            }
            else {
                accordion_trigger.find('.active').addClass('inactive');
                accordion_trigger.find('.active').removeClass('active');
                $(this).removeClass('inactive');
                $(this).addClass('active');
            }
            event.preventDefault();
        });
    };

    /* ==================================================
     Toggle
     ================================================== */

    BRUSHED.toggle = function () {
        var accordion_trigger_toggle = $('.accordion-heading.togglize');

        accordion_trigger_toggle.delegate('.accordion-toggle', 'click', function (event) {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
                $(this).addClass('inactive');
            }
            else {
                $(this).removeClass('inactive');
                $(this).addClass('active');
            }
            event.preventDefault();
        });
    };

    /* ==================================================
     Tooltip
     ================================================== */

    BRUSHED.toolTip = function () {
        $('a[data-toggle=tooltip]').tooltip();
    };


    /* ==================================================
     Init
     ================================================== */

    BRUSHED.slider();

    $(document).ready(function () {
        Modernizr.load([
            {
                test: Modernizr.placeholder,
                nope: '/staticfiles/js/placeholder.js',
                complete: function () {
                    if (!Modernizr.placeholder) {
                        Placeholders.init({
                            live: true,
                            hideOnFocus: false,
                            className: "yourClass",
                            textColor: "#999"
                        });
                    }
                }
            }
        ]);

        // Preload the page with jPreLoader
        $('body').jpreLoader({
            splashID: "#jSplash",
            showSplash: true,
            showPercentage: true,
            autoClose: true,
            splashFunction: function () {
                $('#circle').delay(250).animate({'opacity': 1}, 500, 'linear');
            }
        });

        BRUSHED.nav();
        BRUSHED.mobileNav();
        BRUSHED.listenerMenu();
        BRUSHED.menu();
        BRUSHED.goSection();
        BRUSHED.goUp();
        BRUSHED.filter();
        BRUSHED.fancyBox();
        BRUSHED.contactForm();
        BRUSHED.tweetFeed();
        BRUSHED.scrollToTop();
        BRUSHED.utils();
        BRUSHED.accordion();
        BRUSHED.toggle();
        BRUSHED.toolTip();
    });

    $(window).resize(function () {
        BRUSHED.mobileNav();
    });

});

function beforeSend(xhr, settings) {
    function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            if (!(/^http:.*!/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
}

$("#send-invitation").click(function () {
    $.ajax({
        url: '/core/team/invitation',
        data: JSON.stringify({user_id: $('#curr-user-id').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                alert('Invite has been sent')
            }
            else if (xhr.status == 202) {
                alert('The invitation had been already sent');
            }
            else {
                alert('Something wrong, please try again or write a feedback');
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});


$(".button-accept").click(function () {
    var me = this;
    $.ajax({
        url: '/core/team/invitation/accept',
        data: JSON.stringify({team_name: $(this).siblings('.team-name').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                me.parentElement.remove();
                check_invitations();
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});

$(".button-decline").click(function () {
    var me = this;
    $.ajax({
        url: '/core/team/invitation/decline',
        data: JSON.stringify({team_name: $(this).siblings('.team-name').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                me.parentElement.remove();
                check_invitations();
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});

function check_invitations() {
    var inv = $(document).find('.invitations');
    if (inv.length == 0) {
        var info_text = $(document).find('.info-text').first();
        info_text.append('<p>You have no invitations yet</p>')
    }
}


$("#signup-team-competition").click(function () {
    $.ajax({
        url: '/core/competition/signup/team',
        data: JSON.stringify({competition_id: $('#curr-competition-id').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            setTimeout(function () {

                    location.reload();
                }, 1000);
            if (xhr.status == 200) {
                alert('You have been register your team!')
            }
            else if (xhr.status == 202) {
                alert('The invitation had been already sent');
            }
            else {
                alert('Something wrong, please try again or write a feedback');
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});

$("#signout-team-competition").click(function () {
    $.ajax({
        url: '/core/competition/signup/team',
        data: JSON.stringify({competition_id: $('#curr-competition-id').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            setTimeout(function () {

                    location.reload();
                }, 1000);
            if (xhr.status == 200) {
                alert('Invite has been sent')
            }
            else if (xhr.status == 202) {
                alert('The invitation had been already sent');
            }
            else {
                alert('Something wrong, please try again or write a feedback');
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});

$("#signout-user-competition").click(function () {
    $.ajax({
        url: '/core/competition/signout/user',
        data: JSON.stringify({competition_id: $('#curr-competition-id').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            setTimeout(function () {

                    location.reload();
                }, 1000);
            if (xhr.status == 200) {
                alert('Invite has been sent')
            }
            else if (xhr.status == 202) {
                alert('The invitation had been already sent');
            }
            else {
                alert('Something wrong, please try again or write a feedback');
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});

$("#signup-user-competition").click(function () {
    $.ajax({
        url: '/core/competition/signup/user',
        data: JSON.stringify({competition_id: $('#curr-competition-id').text()}),
        contentType: "application/json; charset=utf-8",
        processData: false,
        type: 'POST',
        success: function (response, textStatus, xhr) {
            setTimeout(function () {

                    location.reload();
                }, 1000);
            if (xhr.status == 200) {
                alert('Invite has been sent')
            }
            else if (xhr.status == 202) {
                alert('The invitation had been already sent');
            }
            else {
                alert('Something wrong, please try again or write a feedback');
            }
        },
        beforeSend: function (xhr, settings) {
            beforeSend(xhr, settings)
        }
    });
});