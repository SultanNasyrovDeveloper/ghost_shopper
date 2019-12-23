axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';


// HELPER FUNCTIONS
let formToJson = function (form) {
    let formData = form.serializeArray();
    let data = {};
    $(formData ).each(function(index, obj){
        if (obj.value !== "NaN") {
            data[obj.name] = obj.value;}});
    return data
};

let vm = new Vue({
    el: '#chat',
    delimiters : ["[[", "]]"],
    data: {
        chat: JSON.parse(chat),
    },
    methods: {
        sendMessage: async function (event) {
            const form = $('#message-form');
            const serializedFormData = formToJson(form);
            const url = form.attr('action');
            try {
                const { data } = await axios.post(url, {form_data: serializedFormData});
                if (data.status === 200) {
                    this.chat.messages.push(data.message);
                }
            } catch (e) {
                console.log(e);
                return {};
            }

        },
        refreshChat: async function () {
            const messagesCount = this.chat.messages.length;
            let lastMessageDateTime;

            if (messagesCount < 1) {
                lastMessageDateTime = null;
            } else {
                lastMessageDateTime = this.chat.messages[messagesCount-1].creation_datetime;
            }

            try {
                const { data } = await axios.post(refreshUrl, {
                    last_message_datetime: lastMessageDateTime,
                    chat_id: this.chat.id
                });
                if (data.status === 200) {
                    if (data.new_messages_exist) {
                        this.chat.messages.push(...data.new_messages)
                    }
                }
            } catch (e) {
                console.log(e);
                return {};
            }

        },
    }

});