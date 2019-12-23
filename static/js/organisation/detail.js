$(document).ready(function () {

    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';

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

    let createComment = async function (url, formData) {
        try {
            const { data } = await axios.post(url, {form_data: formData});
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };

    let getCommentHTML = function (commentData) {
        let comment = `
            <div class="media m-1 comment">
                <div class="mr-3">
                    <a href="${commentData.authorUrl}">
                        <img src="${commentData.authorImageUrl}" class="rounded-circle" width="42" height="42" alt="">           
                    </a>
                </div>

                <div class="media-body">
                    <div class="d-flex justify-content-between">
                        <a href="${commentData.authorUrl}">${commentData.authorName}</a>
                    </div>
                    ${commentData.body}
                    <div class="d-flex">
                        <span class="font-size-sm text-muted d-flex align-items-center">${commentData.created}</span>
                        <form class="delete-comment" action="/chat/${Number(commentData.id)}/delete-comment" method="post">
                            <button type="submit" class="btn bg-transparent"><i class="icon-trash text-danger"></i></button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        return comment
    };

    let collapseCard = function (target) {
        let $target = target, slidingSpeed = 150;
        $target.toggleClass('card-collapsed');
        $target.find('[data-action=collapse]').toggleClass('rotate-180');
        $target.children('.card-header').nextAll().slideToggle(slidingSpeed);
    };

    let deleteComment = async function (url) {
        try {
            const { data } = await axios.post(url);
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    };

    let deleteMessage = async function (url) {
        try {
            const { data } = await axios.post(url);
            return data;
        } catch (e) {
            console.log(e);
            return {};
        }
    } ;

    $(document).on('submit', '.comment-form', async function(e) {
        e.preventDefault();
        const url = $(this).attr('action');
        const formData = formToJson($(this));
        const response = await createComment(url, formData);

        if (response.status === 200) {
            let commentContainer = $(this).closest('.message').find('.comments');
            let comment = getCommentHTML(response.commentData);
            commentContainer.append(comment);
            $(this)[0].reset();
            let card = $(this).closest('.card');
            if (card.hasClass('card-collapsed')) {
                collapseCard(card);
            }
        }
    });

    $(document).on('submit', '.delete-comment', async function (e) {
        e.preventDefault();
        const url = $(this).attr('action');
        const response = await deleteComment(url);

        if (response.status === 200) {
            let comment = $(this).closest('.comment');
            comment.remove();
        }
    });

    $(document).on('submit', '.delete-message', async function (e) {
        e.preventDefault();
        const url = $(this).attr('action');
        const response = await deleteMessage(url);

        if (response.status === 200) {
            let message = $(this).closest('.message').remove()
        }
    });
});