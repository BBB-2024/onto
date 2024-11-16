const app = Vue.createApp({
    data() {
      return {
        teamCode: localStorage.getItem('teamCode') || '',
        tasks: [],
        selectedTask: null,
      };
    },
    methods: {
      saveTeamCode() {
        localStorage.setItem('teamCode', this.teamCode);
        alert('Team Code saved successfully!');
      },
      async loadTasks() {
        if (!this.teamCode) {
          alert('Please enter a valid team code!');
          return;
        }
        const response = await this.apiRequest('gettasks.php', { id: 'all' });
        if (response.status === 'success') {
          this.tasks = response.data.task_list;
        } else {
          alert(response.message || 'Failed to load tasks.');
        }
      },
      async viewTaskDetails(taskId) {
        const response = await this.apiRequest('gettasks.php', { id: taskId });
        if (response.status === 'success') {
          this.selectedTask = response.data;
          console.log("Task", response.data);
        } else {
          alert(response.message || 'Failed to load task details.');
        }
      },
      async submitTaskAnswers() {
        if (!this.selectedTask) return;
  
        const answers = this.selectedTask.questions.map((q) => ({
          id: q.ID,
          answer: this.calculateAnswer(q.params),
        }));
  
        const response = await this.apiRequest(
          'answer.php',
          {
            id: this.selectedTask.ID,
            original_data: this.selectedTask,
            original_hash: this.selectedTask.hash,
            answer_data: answers,
          },
          true
        );
  
        if (response.status === 'success') {
          alert('Answers submitted successfully!');
        } else {
          alert(response.message || 'Failed to submit answers.');
        }
      },
      calculateAnswer(params) {
        const { type, number1, number2 } = params;
        switch (type) {
          case 'ADDITION':
            return number1 + number2;
          case 'SUBTRACTION':
            return number1 - number2;
          default:
            return null;
        }
      },
      async apiRequest(endpoint, data, isAnswer = false) {
        const url = `http://bitkozpont.mik.uni-pannon.hu/2024/${endpoint}`;
        const payload = { ...data, teamcode: this.teamCode };
        if (isAnswer) {
          payload.original_data = data.original_data;
          payload.original_hash = data.original_hash;
          payload.answer_data = data.answer_data;
        }
        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          return await response.json();
        } catch (error) {
          console.error(error);
          return { status: 'error', message: 'API request failed.' };
        }
      },
    },
  });
  
  app.mount('#app');
  