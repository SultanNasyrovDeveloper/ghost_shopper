

$(document).ready(function() {
    $('.summernote').summernote({
        toolbar: [
            // [groupName, [list of button]]
            ['style', ['bold', 'italic', 'underline', 'clear']],
        ]
    });
});

    //
    const addSectionUrl = $('#create-section-form').attr('action');
    const deleteSectionUrl = $('.delete-section').attr('data-href');
    const deleteQuestionUrl = $('.delete-question-button').attr('data-url');
    const deleteOptionUrl = $('.delete-option').attr('data-url');
     //
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';

    // HELPER FUNCTIONS
    let formToJson = function (form) {
        let formData = form.serializeArray();
        let data = {};
        $(formData ).each(function(index, obj){
            if (obj.value !== "NaN") {
                data[obj.name] = obj.value;
            }
        });
        return data
    };

    // VUE APP
    let vm = new Vue({
        el: '#app',
        delimiters: ["[[", "]]"],
        data: {
            checklist: JSON.parse(checklist),
            questionTypes: JSON.parse(questionTypesJson),

            formErrors: null,
            upperSectionId: null,
            newQuestionSectionId: null,
            newQuestionType: null,
            upperQuestionId: null,
            newOptionQuestionId: null,
            optionCreateErrors: null,
            upperOptionId: null,
            parentSectionId: null,
        },
        mounted: function deleteLoader () {
            $('.loader-container').remove();
        },
        methods: {
            // helpers
            getSectionById: function (sectionId) {
                let target;
                for (let section of this.checklist.sections) {
                    if (section.id === sectionId) {
                        target = section;
                        return target
                    }
                }
                if (target === undefined) {
                    for (let section of this.checklist.sections) {
                        for (let subsection of section.subsections) {
                            if (subsection.id === sectionId) {
                                target = subsection;
                                return target;
                            }

                        }
                    }
                }
            },
            getQuestionById: function (questionId) {
                let target;
                for (let section of this.checklist.sections) {
                    for (let question of section.questions) {
                        if (question.id === questionId) {
                            target = question;
                            return target;
                        }

                    }
                    for (let subsection of section.subsections) {
                        for (let question of subsection.questions) {
                            if (question.id === questionId) {
                                target = question;
                                return target;
                            }
                        }
                    }
                }
                return target;
            },
            prepareUpperSectionId: function(event) {
                this.upperSectionId = Number(event.target.dataset.sectionId);
            },
            prepareQuestionCreation: function (event) {
                this.newQuestionSectionId = Number(event.target.dataset.sectionId);
                this.newQuestionType = event.target.dataset.questionType
            },
            prepareBelowQuestionCreation: function (event) {
                this.newQuestionSectionId = Number(event.target.dataset.sectionId);
                this.newQuestionType = event.target.dataset.questionType;
                this.upperQuestionId = event.target.dataset.questionId;
            },
            prepareOptionCreation: function (event) {
                this.newOptionQuestionId = Number(event.target.dataset.questionId);
                this.upperOptionId = Number(event.target.dataset.optionId);
            },
            prepareSectionCreation: function (event) {
                this.upperSectionId = event.target.dataset.sectionId;
            },
            prepareSubsectionCreation: function (event) {
                this.parentSectionId = event.target.dataset.sectionId;
                this.upperSectionId = event.target.dataset.upperSection;
            },
            cleanupSectionCreationForm: function () {
                this.upperSectionId = null;
                this.parentSectionId = null;
                this.formErrors = null;
            },
            cleanupQuestionCreationForm: function () {
                this.newQuestionType = null;
                this.upperQuestionId = null;
                this.formErrors = null;
            },
            cleanupOptionCreationForm: function () {
                this.newOptionQuestionId = null;
                this.upperOptionId = null;
                this.formErrors = null;
            },
            addSection: function (section, upperSectionId, parentSectionId) {
                if (parentSectionId) {
                    // add subsection
                    let parentSection = this.getSectionById(parentSectionId);

                    if (upperSectionId) {
                        // add subsection below upper section
                        for (let i = 0; i < parentSection.subsections.length; i++) {
                            if (parentSection.subsections[i].id === upperSectionId) parentSection.subsections.splice(i+1, 0, section);
                        }
                    } else {
                        // add subsection in the end of sections list
                        parentSection.subsections.push(section);
                    }
                } else {
                    // add section
                    if (upperSectionId) {
                        // add section below upper section
                        for (let i = 0; i < this.checklist.sections.length; i++) {
                            if (this.checklist.sections[i].id === upperSectionId) this.checklist.sections.splice(i+1, 0, section);
                        }
                    } else {
                        // add section in the end of sections list
                        this.checklist.sections.push(section);
                    }
                }
            },

            // handlers
            createSection: async function () {
                // serialize section creation form and handle it on the back
                let form = $('#create-section-form');
                let serializedForm = formToJson(form);
                let response = await createSection(serializedForm);

                // handle back response
                if (response.status === 200) {
                    let section = JSON.parse(response.section);
                    this.addSection(section, response.upper_section, section.parent);
                    $('#create-section-modal').modal('hide');
                    this.cleanupSectionCreationForm();
                    form[0].reset();
                } else {
                    // if response status not ok show error message
                    this.formErrors = response.errors;
                }

            },
            deleteSection: async function (event) {
                let sectionId = Number(event.target.dataset.sectionId);
                let serverResponse = await deleteSection(sectionId);
                if (serverResponse.status === 200) {
                    for (let i = 0; i < this.checklist.sections.length; i++) {
                        let section = this.checklist.sections[i];
                        if (section.id === sectionId) {
                            this.checklist.sections.splice(i, 1);
                            return
                        }
                    }
                    for (let section of this.checklist.sections) {
                        for (let i = 0; i < section.subsections.length; i++) {
                            if (section.subsections[i].id === sectionId) {
                                section.subsections.splice(i, 1);
                                return;
                            }
                        }
                    }
                }
            },
            createQuestion: async function (event) {
                let button = event.target;
                let modal = $(button.closest('.modal'));
                let questionData = formToJson(modal.find('.question-creation-form'));
                let answerData = formToJson(modal.find('.answer-creation-form'));
                let url = modal.attr('data-create-url');
                let response = await createQuestion(questionData, answerData, url);
                if (response.status === 200) {
                    let question = response.question;
                    let targetSection = this.getSectionById(question.section);

                    if (response.upper_question) {
                        for(let i = 0; i < targetSection.questions.length; i++){
                            let currentQuestion = targetSection.questions[i];
                            if (currentQuestion.id === Number(response.upper_question)) {
                                targetSection.questions.splice(i+1, 0, question);
                            }}
                    } else {
                        targetSection.questions.push(question);
                    }

                    modal.modal('hide');
                    this.cleanupQuestionCreationForm();
                    let widget = modal.find('.summernote');
                    widget.summernote('reset');

                } else {
                    this.formErrors = response.errors;
                }
            },
            deleteQuestion: async function (event) {
                //
                const questionId = Number(event.target.dataset.questionId);
                const serverResponse = await deleteQuestion(questionId);
                const section = this.getSectionById(serverResponse.section_id);
                //
                for(let i = 0; i < section.questions.length; i++){
                    let question = section.questions[i];
                    if (question.id === serverResponse.question_id) {
                        section.questions.splice(i, 1);
                    }
                }

            },
            createOption: async function (event) {
                let button = event.target;
                let modal = $(button.closest('.modal'));
                let optionData = formToJson(modal.find('.option-form'));
                let url = modal.attr('data-create-url');
                let response = await createOption(optionData, url);
                if (response.status === 200) {
                    let question = this.getQuestionById(response.option.question);
                    let upperOptionId = Number(response.upper_option);
                    if (upperOptionId) {
                        for (let i = 0; i < question.options.length; i++) {
                            if (question.options[i].id === upperOptionId) {
                                question.options.splice(i+1, 0, response.option)
                            }
                        }
                    } else {
                        question.options.push(response.option)
                    }

                    modal.modal('hide');
                    this.cleanupOptionCreationForm();

                } else {

                }
            },
            deleteOption: async function (event) {
                //
                const optionId = Number(event.target.dataset.optionId);
                const questionType = event.target.dataset.questionType;
                const serverResponse = await deleteOption(optionId, questionType);

                if (serverResponse.status === 200) {
                    let question = this.getQuestionById(serverResponse.question_id);
                    for (let i = 0; i < question.options.length; i++ ) {
                        if (question.options[i].id === serverResponse.option) question.options.splice(i, 1);
                    }
                }

            },

        },

    });

    // CREATE NEW SECTION
    let createSection = async function (sectionData) {
        try {
            const { data } = await axios.post(addSectionUrl, {form_data: sectionData});
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }

    };

    // DELETE SECTION
    let deleteSection = async function (sectionId) {
        try {
            const { data } = await axios.post(deleteSectionUrl, {section_id: sectionId})
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };

    // CREATE QUESTION
    let createQuestion = async function (questionData, answerData, url) {
        try {
            const { data } = await axios.post(url, {question_data: questionData, answer_data: answerData})
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }

    };

    // DELETE QUESTION
    let deleteQuestion = async function (questionId) {
        try {
            const { data } = await axios.post(deleteQuestionUrl, {question_id: questionId})
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };

    // CREATE OPTION
    let createOption = async function (optionData, url) {
        try {
            const { data } = await axios.post(url, {option_data: optionData})
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };

    // DELETE OPTION
    let deleteOption = async function (optionId, questionType) {
        try {
            const { data } = await axios.post(deleteOptionUrl, {option_id: optionId, question_type: questionType});
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };
