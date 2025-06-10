$(document).ready(function () {
    function fetchBooks(query = '', searchType = 'title') {
    $.ajax({
        url: "/books/ajax/book-search/",
        data: {
            'q': query,
            'type': searchType
        },
        dataType: 'json',
        success: function (data) {
            $('#book-container').empty();
            if (data.books.length > 0) {
                data.books.forEach(function (book) {
                    const bookHtml = `
                        <div class="book-card">
                            ${book.cover_image ? `<img src="${book.cover_image}" alt="Обложка книги">` : ''}
                            <p><strong>${book.title}</strong></p>
                            <p>${book.author}</p>
                            <div>
                                <button class="like-btn" data-id="${book.id}">👍 ${book.likes || 0}</button>
                                <button class="dislike-btn" data-id="${book.id}">👎 ${book.dislikes || 0}</button>
                            </div>
                            <button class="open-review-modal" data-id="${book.id}" style="margin-top: 10px;">📝 Добавить отзыв</button>
                            <button class="open-view-reviews" data-id="${book.id}" style="margin-top: 5px;">📖 Смотреть отзывы</button>
                        </div>`;
                    $('#book-container').append(bookHtml);
                });
            } else {
                $('#book-container').html('<p>Книги не найдены.</p>');
            }
        },
        error: function () {
            $('#book-container').html('<p>Ошибка загрузки книг.</p>');
        }
    });
}

    // Инициализация поиска
    fetchBooks();

    // Обработчик изменения поискового запроса или типа поиска
    $('#search-box').on('input', function () {
        const query = $(this).val();
        const searchType = $('#search-type').val();
        fetchBooks(query, searchType);
    });

    $('#search-type').on('change', function () {
        const query = $('#search-box').val();
        const searchType = $(this).val();
        fetchBooks(query, searchType);
    });

    $(document).on('click', '.like-btn, .dislike-btn', function () {
        const bookId = $(this).data('id');
        const type = $(this).hasClass('like-btn') ? 'like' : 'dislike';

        $.post("/books/book/reaction/", {
            book_id: bookId,
            type: type,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        }, function () {
            fetchBooks($('#search-box').val());
        }).fail(function () {
            alert('Ошибка обработки реакции.');
        });
    });

    $(document).on('click', '.open-review-modal', function () {
        const bookId = $(this).data('id');
        $('#modalBookId').val(bookId);
        $('#modalReviewText').val('');
        $('#reviewModal').fadeIn();
    });

    $(document).on('click', '.close-modal', function () {
        $(this).closest('.modal').fadeOut();
    });

    $(window).click(function (e) {
        if ($(e.target).hasClass('modal')) {
            $('.modal').fadeOut();
        }
    });

    $('#reviewModalForm').submit(function (e) {
        e.preventDefault();
        const bookId = $('#modalBookId').val();
        const review = $('#modalReviewText').val();

        $.post("/books/book/review/", {
            book_id: bookId,
            review: review,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        }, function () {
            alert('Спасибо за отзыв!');
            $('#reviewModal').fadeOut();
            fetchBooks($('#search-box').val());
        }).fail(function () {
            alert('Ошибка отправки отзыва.');
        });
    });

    $(document).on('click', '.open-view-reviews', function () {
        const bookId = $(this).data('id');

        $.get(`/books/book/${bookId}/reviews/`, function (data) {
            let html = '';
            if (data.reviews.length > 0) {
                data.reviews.forEach(r => {
                    html += `<div style="margin-bottom: 10px;">
                                <strong>${r.reader}</strong><br>
                                <span>${r.comment}</span>
                             </div>`;
                });
            } else {
                html = '<p>Отзывов пока нет.</p>';
            }
            $('#reviewsContent').html(html);
            $('#viewReviewsModal').fadeIn();
        }).fail(function () {
            $('#reviewsContent').html('<p>Ошибка загрузки отзывов.</p>');
            $('#viewReviewsModal').fadeIn();
        });
    });

    // Обработка открытия личного кабинета
    $('#openPersonalCabinet').click(function (e) {
        e.preventDefault();
        $('#personalCabinetModal').fadeIn();
    });
});