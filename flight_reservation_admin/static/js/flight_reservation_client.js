/**
 * @fileOverview Flight reservation administration dashboard. It utilizes the Flight Booking
                 API to handle user information (retrieve user list, edit user profile,
                 as well as add and remove new users form the system). It also
                 permits to list the user reservations, flights templates flights
                 but also to make a reservation and to create a new flight and a new
                 template flight.
 * @author <a href="mailto:jules.larue@student.oulu.fi">Jules Larue</a>
 * @version 1.0
**/


/**** START CONSTANTS****/

/**
 * Set this to true to activate the debugging messages.
 * @constant {boolean}
 * @default
 */
var DEBUG = true;

/**
 * Mason+JSON mime-type
 * @constant {string}
 * @default
 */
const MASONJSON = "application/vnd.mason+json";

const PLAINJSON = "application/json";

/**
 * Link to Users_profile
 * @constant {string}
 * @default
 */
const FLIGHT_BOOKING_SYSTEM_USER_PROFILE = "/profiles/users";

/**
 * Link to Flights profile
 * @constant {string}
 * @default
 */
const FLIGHT_BOOKING_SYSTEM_FLIGHT_PROFILE = "/profiles/flights";

/**
 * Link to Template Flights profile
 * @constant {string}
 * @default
 */
const FLIGHT_BOOKING_SYSTEM_TEMPLATE_FLIGHT_PROFILE = "/profiles/template-flights";

/**
 * Link to Reservations profile
 * @constant {string}
 * @default
 */
const FLIGHT_BOOKING_SYSTEM_RESERVATION_PROFILE = "/profiles/reservations";

/**
 * Default datatype to be used when processing data coming from the server.
 * Due to JQuery limitations we should use json in order to process Mason responses
 * @constant {string}
 * @default
 */
const DEFAULT_DATATYPE = "json";

/**
 * Entry point of the application
 * @constant {string}
 * @default
 */
const ENTRYPOINT = "/flight-booking-system/api/users"; //Entrypoint: Resource Users


/**
 * Associated rel attribute: Users Mason+JSON and users-all
 *
 * Sends an AJAX GET request to retrieve the list of all the users of the application
 *
 * ONSUCCESS=> Show users in the #user_list.
 *             After processing the response it utilizes the method {@link #appendUserToList}
 *             to append the user to the list.
 *             Each user is an anchor pointing to the respective user url.
               When clicking a user, the user data is shown to the right.

 * ONERROR => Show an alert to the user.
 *
 * @author Ivan Sanchez
 * @param {string} [apiurl = ENTRYPOINT] - The url of the Users instance.
**/
function getUsers(apiurl) {
    apiurl = apiurl || ENTRYPOINT;
    $("#mainContent").hide();
    return $.ajax({
        url: apiurl,
        type: 'get',
        dataType:DEFAULT_DATATYPE
    }).always(function(){
        //Remove old list of users
        //clear the form data hide the content information(no selected)
        $("#user_list").empty();
        $("#mainContent").hide();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        //Extract the users
        users = data.items;
        for (var i=0; i < users.length; i++){
            var user = users[i];

            // Append the user to the list that will display his name.
            appendUserToList(user["@controls"].self.href, getFullName(user));
        }

        //Prepare the new_user_form to create a new user
        var create_ctrl = data["@controls"]["flight-booking-system:add-user"]

        if (create_ctrl.schema) {
            createFormFromSchema(create_ctrl.href, create_ctrl.schema, "new_user_form");
        }
        else if (create_ctrl.schemaUrl) {
            $.ajax({
                url: create_ctrl.schemaUrl,
                dataType: DEFAULT_DATATYPE
            }).done(function (data, textStatus, jqXHR) {
                createFormFromSchema(create_ctrl.href, data, "new_user_form");
            }).fail(function (jqXHR, textStatus, errorThrown) {
                if (DEBUG) {
                    console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
                }
                alert_error("Could not fetch form schema. Please, try again");
            });
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Inform user about the error using an alert message.
        alert_error("Could not fetch the list of users.  Please, try again");
    });
}


/**
 * Populate a form with the <input> elements contained in the <i>schema</i> input parameter.
 * The action attribute is filled in with the <i>url</i> parameter. Values are filled
 * with the default values contained in the template. It also marks inputs with required property.
 *
 * @author Ivan Sanchez
 * @param {string} url - The url of to be added in the action attribute
 * @param {Object} schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append <input> elements in the form
 * @param {string} id - The id of the form is gonna be populated
**/
function createFormFromSchema(url,schema,id){
    $form=$('#'+ id);
    $form.attr("action",url);
    //Clean the forms
    $form_content=$(".form_content",$form);
    $form_content.empty();
    $("input[type='button']",$form).hide();
    if (schema.properties) {
        var props = schema.properties;
        Object.keys(props).forEach(function(key, index) {
            if (props[key].type == "object") {
                appendObjectFormFields($form_content, key, props[key]);
            }
            else {
                appendInputFormField($form_content, key, props[key], schema.required.includes(key));
            }

        });
    }
    return $form;
}


/**
 * Private class used by {@link #createFormFromSchema}
 *
 * @author Ivan Sanchez
 * @param {jQuery} container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
**/
function appendInputFormField($container, name, object_schema, required) {
    var input_id = name;
    var prompt = object_schema.title;
    var desc = object_schema.description;

    $input = $('<input type="text" class="form-control"></input>');
    $input.addClass("editable");
    $input.attr('name',name);
    $input.attr('id',input_id);
    $label_for = $('<label></label>');
    $label_for.attr("for",input_id);
    $label_for.text(prompt);

    $container.append($label_for);
    $container.append($input);

    if(desc){
        $input.attr('placeholder', desc);
    }
    if(required){
        $input.prop('required',true);
        $label = $("label[for='"+$input.attr('id')+"']");
        $label.append("*");
    }
}
/**
 * Private class used by {@link #createFormFromSchema}. Appends a subform to append
 * input
 * @author Ivan Sanchez
 * @param {jQuery} $container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
**/
function appendObjectFormFields($container, name, object_schema) {
    $div = $('<div class="subform form-group"></div>');
    $div.attr("id", name);
    Object.keys(object_schema.properties).forEach(function(key, index) {
        if (object_schema.properties[key].type == "object") {
            // only one nested level allowed
            // therefore do nothing
        }
        else {
            appendInputFormField($div, key, object_schema.properties[key], false);
        }
    });
    $container.append($div);
}




/**
 * Helper method that unselects any user from the #user_list and go back to the
 * initial state by hiding the "#mainContent".
**/
function deselectUser() {
    $("#user_list li.active").removeClass("active");
    $("#mainContent").hide();
}




/**
 * Sends an AJAX request to retrieve the information of a user
 * Associated rel attribute: private-data
 *
 * ONSUCCESS =>
 *  a) Extract all the links relations and its corresponding URLs (href)
 *  b) Create a form and fill it with attribute data (semantic descriptors) coming
 *     from the request body. The generated form should be embedded into #user_form.
 *     All those tasks are performed by the method {@link #fillFormWithMasonData}
 *     b.1) If "user:edit" relation exists add its href to the form action attribute.
 *          In addition make the fields editables and use template to add missing
 *          fields.
 *  c) Add buttons to the previous generated form.
 *      c.1) If "user:delete" relation exists show the #deleteUser button
 *      c.2) If "user:edit" relation exists show the #editUser button
 *
 * ONERROR =>
 *   a)Show an alert informing the user profile could not be retrieved and
 *     that the data shown in the screen is not complete.
 *   b)Unselect current user and go to initial state by calling {@link #deselectUser}
 *
 * @param {string} apiurl - The url of the User Profile instance.
**/
function user_data(apiurl){
    return $.ajax({
            url: apiurl,
            dataType:DEFAULT_DATATYPE,
        }).done(function (data, textStatus, jqXHR){
            if (DEBUG) {
            console.log ("#user_data: RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
            }
            //Extract links
            var user_links = data["@controls"];
            var schema, resource_url = null;
            if ("edit" in user_links){
                resource_url = user_links["edit"].href;
                //Extract the template value
                schema = user_links["edit"].schema;
                if (user_links["edit"].schema) {
                    $form = createFormFromSchema(resource_url, schema, "edit_user_form");
                    $("#editUser").show();
                    fillFormWithMasonData($form, data);
                }
                else if (user_links["edit"].schemaUrl) {
                    $.ajax({
                        url: user_links["edit"].schemaUrl,
                        dataType: DEFAULT_DATATYPE
                    }).done(function (schema, textStatus, jqXHR) {
                        $form = createFormFromSchema(resource_url, schema, "edit_user_form");
                        $("#editUser").show();
                        fillFormWithMasonData($form, data);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        if (DEBUG) {
                            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
                        }
                        alert_error("Could not fetch form schema.  Please, try again");
                    });
                }
                else {
                    alert_error("Form schema not found");
                }
            }

        }).fail(function (jqXHR, textStatus, errorThrown){
            if (DEBUG) {
                console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
            }
            //Show an alert informing that I cannot get info from the user.
            alert_error("Cannot extract all the information about this user from the server");
            deselectUser();
        });
}




/**
 * Sends an AJAX request to retrieve information related to a User {@link http://docs.flightreservationapp1.apiary.io/#reference/users/user}
 *
 * Associated link relation:self (inside the user profile)
 *
 *  ONSUCCESS =>
 *              a) Fill basic user information: Full name and registrationdate.
 *              b) Extract associated link relations from the response
 *                    b.1) If user:delete: Show the #deleteUser button. Add the href
 *                        to the #user_form action attribute.
 *                    b.2) If user:edit: Show the #editUser button. Add the href
 *                        to the #user_form action attribute.
 *                    b.3) If user: data: Call the function {@link #user_data} to
 *                        extract the information of the profile
 *                    b.4) If user:reservations: Call the function {@link #reservations_history} to extract
 *                        the reservations history of the current user.  *
 *
 * ONERROR =>   a) Alert the user
 *              b) Unselect the user from the list and go back to initial state
 *                (Call {@link deleselectUser})
 *
 * @author Ivan Sanchez
 * @param {string} apiurl - The url of the User instance.
**/
function get_user(apiurl) {
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false,
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        //Set right url to the user form
        $("#user_form").attr("action",apiurl);
        // FIll the registration date
        $("#registrationdate").val(millisToStringDate(data.registrationdate || 0));
        delete(data.registrationdate);
        $("#reservationsNumber").text("??");

        //Extract user information
        var user_links = data["@controls"];
        if ("flight-booking-system:delete" in user_links){
                resource_url = user_links["flight-booking-system:delete"].href; // User delete link
                $("#deleteUser").show();
            }
        //Extracts urls from links. I need to get if the different links in the
        //response.
        if ("flight-booking-system:reservations-history" in user_links){
            var reservations_url = user_links["flight-booking-system:reservations-history"].href;
        }

        // Fill user data
        if (resource_url) {
          user_data(resource_url);
        }

        // TODO Fill reservations history (if time to do it)


    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert_error("Cannot extract information about this user from the flight booking system service.");
        //Deselect the user from the list.
        deselectUser();
    });
}



/**
  * Sends an AJAX request to add a user to the API.
  * Makes use of the HTTP POST method.
  * ONSUCCESS =>
  *             1) Show an alert to the user to inform that user has been added
  *             2) Reloads the list of all the users to display
  *
  * ONERROR => Displays a message to the user to inform him that
  *           could not be added to the system
  * @param api_url the url of the Users resource to add a new use
  * @param new_user_info an associative aray containing the information
  *                     of the new user to add
  */
function add_user(api_url, new_user_info) {
  console.log("user data: " + JSON.stringify(new_user_info))
  $.ajax({
    url: api_url,
    type: "POST",
    data: JSON.stringify(new_user_info),
    processData:false,
    contentType: PLAINJSON
  }).done(function (data, textStatus, jqXHR){
    if (DEBUG) {
        console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
    }

    // Inform user that the user has been deleted
    alert_success("The user with has been deleted from the system.");

    // Update the users list from the server
    getUsers();
  }).fail(function (jqXHR, textStatus, errorThrown){
    if (DEBUG) {
        console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
    }

    // Inform the user that user has NOT been deleted
    alert_error("Error while trying to delete the user from the database.");
  });
}



/**
  * Sends an AJAX request to delete a user from the API.
  * Makes use of the HTTP DELETE method.
  * ONSUCCESS =>
  *             1) Show an alert to the user to inform him that deletion was successful
  *             2) Reloads the list of all the users to display
  *
  * ONERROR => Displays a message to the user to inform him that user
  *           could not be deleted
  * @param api_url the url of the user resource to delete
  */
function delete_user(api_url) {
  console.log("DElete Url : " + api_url)
  $.ajax({
    url: api_url,
    type: 'DELETE'
  }).done(function (data, textStatus, jqXHR){
    if (DEBUG) {
        console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
    }

    // Inform user that the user has been deleted
    alert_success("The user with has been deleted from the system.");

    // Update the users list from the server
    getUsers();
  }).fail(function (jqXHR, textStatus, errorThrown){
    if (DEBUG) {
        console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
    }

    // Inform the user that user has NOT been deleted
    alert_error("Error while trying to delete the user from the database.");
  });
}

/**
  * Sends an AJAX request to update the information of a user.
  * Makes use of the HTTP PUT method.
  *
  * ONSUCCESS =>
  *               1) Show an alert to the user to inform him that update was successful
  *               2) Reloads the list of all users
  *
  * ONERROR => Displays a message to the user to inform him that user
  *           data could not be updated
  * @param api_url the url of the user resource to update
  * @param updated_user_data an associative array containing the new
  *                         information of the user
  */
function edit_user(api_url, updated_user_data) {
  $.ajax({
    url: api_url,
    type: "PUT",
    data: JSON.stringify(updated_user_data),
    processData:false,
    contentType: PLAINJSON
  }).done(function (data, textStatus, jqXHR){
    if (DEBUG) {
        console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
    }

    // Inform user that the user has been deleted
    alert_success("The user data has been successfully.");

    // Reload the list of users
    getUsers();

  }).fail(function (jqXHR, textStatus, errorThrown){
    if (DEBUG) {
        console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
    }

    // Inform the user that user has NOT been deleted
    alert_error("Error while trying to update the user data.");
  });
}


/**
 * Append a new user to the #user_list. It appends a new <li> element in the #user_list
 * using the information received in the arguments.
 *
 * @author Ivan Sanchez
 * @param {string} url - The url of the User to be added to the list
 * @param {string} user - The name of the user to display in the users list
 * @returns {Object} The jQuery representation of the generated <li> elements.
**/
function appendUserToList(url, userName) {
    var $user = $('<li class="nav-item">').html('<a class= "user_link nav-link " href="' + url + '">'
      + '<span class="oi oi-person"></span>' + userName + '</a>');
    //Add to the user list
    $("#user_list").append($user);
    return $user;
}




/**
 * Helper method to visualize the form to create a new user (#new_user_form)
 * It hides current user information and purge old data still in the form. It
 * also shows the #createUser button.
 * @author Ivan Sanchez
**/
function showNewUserForm () {
    //Remove selected users in the sidebar
    deselectUser();

    //Hide the user data, show the newUser div and reset the form
    $("#userData").hide();
    var form =  $("#new_user_form")[0];
    form.reset();
    // Show butons
    $("input[type='button']",form).show();

    $("#newUser").show();
    //Be sure that #mainContent is visible.
    $("#mainContent").show();
}






/**** BUTTON HANDLERS ****/

/**
 * Shows in #mainContent the #new_user_form. Internally it calls to {@link #showNewUserForm}
 *
 * TRIGGER: #addUserButton
**/
function handleShowUserForm(event){
    if (DEBUG) {
        console.log ("Triggered handleShowUserForm");
    }
    //Show the form. Note that the form was updated when I apply the user collection
    showNewUserForm();
    return false;
}



/**
 * Uses the API to delete the currently active user.
 *
 * TRIGGER: #deleteUser
**/
function handleDeleteUser(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleDeleteUser");
    }

    var userurl = $(this).closest("form").attr("action");
    delete_user(userurl);
    return false;
}

/**
 * Uses the API to update the user's profile with the form attributes in the present form.
 *
 * TRIGGER: #editUser
**/
function handleEditUser(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleEditUser");
    }
    var $form = $(this).closest("form");
    var body = serializeFormTemplate($form);
    var user_url = $(this).closest("form").attr("action");
    edit_user(user_url, body);
    return false;
}

/**
 * Uses the API to create a new user with the form attributes in the present form.
 *
 * TRIGGER: #createUser
**/
function handleCreateUser(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateUser");
    }
    var $form = $(this).closest("form");
    var template = serializeFormTemplate($form);
    var url = $form.attr("action");
    add_user(url, template);
    return false; //Avoid executing the default submit
}


/**
 * Uses the API to retrieve user's information from the clicked user. In addition,
 * this function modifies the active user in the #user_list (removes the .active
 * class from the old user and add it to the current user)
 *
 * TRIGGER: click on #user_list li a
**/
function handleGetUser(event) {
    if (DEBUG) {
        console.log ("Triggered handleGetUser");
    }

    event.preventDefault();
    $("#user_list li").removeClass("active");

    // Make the user element 'active' visually
    $(this).parent().addClass("active");

    prepareUserDataVisualization();

    var url = $(this).attr("href");
    get_user(url);

    return;
}



/***** UTIL FUNCTION *****/

/**
  * Gets the full name (first name + last name) of a user
  */
function getFullName(user) {
  return user.firstName + " " + user.lastName;
}


function millisToStringDate(millis) {
  var date = new Date(millis);

  // dd.MM.YYYY hh:mm
  return addZeroIfLowerThanTen(date.getDate()) + "."
      + addZeroIfLowerThanTen(date.getMonth() + 1) + "."
      + date.getFullYear() + " "
      + addZeroIfLowerThanTen(date.getHours()) + ":"
      + addZeroIfLowerThanTen(date.getMinutes());
}

function addZeroIfLowerThanTen(digit) {
  if (digit >= 0 && digit < 10) {
    return "0" + digit;
  } else {
    return digit;
  }
}


/**
 * Populate a form with the content in the param <i>data</i>.
 * Each data parameter is going to fill one <input> field. The name of each parameter
 * is the <input> name attribute while the parameter value attribute represents
 * the <input> value. All parameters are by default assigned as
 * <i>readonly</i>.
 *
 * NOTE: All buttons in the form are hidden. After executing this method adequate
 *       buttons should be shown using $(#button_name).show()
 *
 * @author Ivan Sanchez
 * @param {jQuery} $form - The form to be filled in
 * @param {Object} data - An associative array formatted using Mason format ({@link https://tools.ietf.org/html/draft-kelly-json-hal-07})
**/

function fillFormWithMasonData($form, data) {

    $(".form_content", $form).children("input").each(function() {
        if (data[this.id]) {
            $(this).attr("value", data[this.id]);
        }
    });

    $(".form_content", $form).children(".subform").children("input").each(function() {
        var parent = $(this).parent()[0];
        if (data[parent.id][this.id]) {
            $(this).attr("value", data[parent.id][this.id]);
        }
    });
}



/**
 * Serialize the input values from a given form (jQuery instance) into a
 * JSON document.
 *
 * @author Ivan Sanchez
 * @param {Object} $form - a jQuery instance of the form to be serailized
 * @returs {Object} An associative array in which each form <input> is converted
 * into an element in the dictionary.
**/
function serializeFormTemplate($form){
    var envelope={};
    // get all the inputs into an array.
    var $inputs = $form.find(".form_content input");
    $inputs.each(function() {
        envelope[this.id] = $(this).val();
    });

    var subforms = $form.find(".form_content .subform");
    subforms.each(function() {

        var data = {}

        $(this).children("input").each(function() {
            data[this.id] = $(this).val();
        });

        envelope[this.id] = data
    });
    return envelope;
}


/**
 * Helper method to be called before showing new user data information
 * It purges old user's data and hide all buttons in the user's forms (all forms
 * elements inside teh #userData)
 *
**/
function prepareUserDataVisualization() {

    //Remove all children from form_content
    $("#userProfile .form_content").empty();
    //Hide buttons
    $("#userData .commands input[type='button'").hide();
    //Reset all input in userData
    $("#userData input[type='text']").val("??");
    //Remove old messages
    $("#reservations_list").empty();
    //Be sure that the newUser form is hidden
    $("#newUser").hide();
    //Be sure that user information is shown
    $("#userData").show();
    //Be sure that mainContent is shown
    $("#mainContent").show();
}



/***** NOTIFICATIONS FUNCTIONS *****/

function alert_success(message) {
  Lobibox.notify('success', {
    delayIndicator: false,
    msg: message
  });
}


function alert_error(message) {
  Lobibox.notify('error', {
    delayIndicator: false,
    msg: message
  });
}


$(function() {
  // When document is ready


  $("#addUserButton").on("click",  handleShowUserForm);
  $("#deleteUser").on("click", handleDeleteUser);
  $("#editUser").on("click", handleEditUser);
  $("#createUser").on("click", handleCreateUser);

  $("#user_list").on("click", "li a", handleGetUser);

  $.get({
    url: 'localhost:5000/flight-booking-system/api/users',
    success: function() { alert("Test Success") }
  });
  getUsers(ENTRYPOINT);
})
