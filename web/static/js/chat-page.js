const { createApp, ref } = Vue

createApp({
    setup() {
        const patients = ref(JSON.parse(JSON.parse(document.getElementById('patient-list').textContent)));
        const chatList = ref(JSON.parse(JSON.parse(document.getElementById('chat-list').textContent)));

        const currentPatient = ref(null);
        const chats = ref([]);
        const message = ref('');

        const setCurrentPatient = (patient) => {
            currentPatient.value = patient;
            chats.value = chatList.value.filter(chat => chat.patient_id == patient.user_id);
        }

        const sendMessage = () => {
            window.chatSocket.send(JSON.stringify({ 
                message: message.value,
                receiver_id: currentPatient.value.user_id,
                type: 'text'
             }))
        }

        setCurrentPatient(patients.value[0]);


        window.chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type == 'chat_message') {
                chatList.value.push(data);
                chats.value.push(data);
                message.value = '';
            }
        }

        return {
            currentPatient, patients, chats, message, sendMessage
        }
    }
}).mount('#chat_page')