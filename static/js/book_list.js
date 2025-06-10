$(function () {
    function updateBooks() {
        const searchType = $('#search-type').val();
        const searchTerm = $('#search-box').val();

        $.get("/books/ajax-book-list/", {
            type: searchType,
            q: searchTerm
        }, function (data) {
            $('.book-container').html(data.html);
            bindCardClickEvents(); // Привязываем события после обновления
        }).fail(function (xhr) {
            console.error('Ошибка при загрузке книг:', xhr.responseText);
        });
    }

    function bindCardClickEvents() {
        $('.book-card').off('click').on('click', function (e) {
            if ($(e.target).hasClass('delete-icon') || $(e.target).closest('.delete-icon').length) {
                return;
            }
            const bookId = $(this).data('book-id');
            const quantity = parseInt($(this).find('p:contains("Количество:")').text().replace('Количество:', '').trim());
            if (quantity > 1) {
                const inventoryList = $(this).data('inventory').split(',').map(item => `<li>${item.trim()}</li>`).join('');
                $('#inventory-book-title').text($(this).find('strong').text());
                $('#inventory-items').html(inventoryList);
                $('#modalInventory').css('display', 'flex');
            }
        });

        $('.show-inventories').off('click').on('click', function (e) {
            e.preventDefault();
            const bookCard = $(this).closest('.book-card');
            const quantity = parseInt(bookCard.find('p:contains("Количество:")').text().replace('Количество:', '').trim());
            if (quantity > 1) {
                const inventoryList = bookCard.data('inventory').split(',').map(item => `<li>${item.trim()}</li>`).join('');
                $('#inventory-book-title').text(bookCard.find('strong').text());
                $('#inventory-items').html(inventoryList);
                $('#modalInventory').css('display', 'flex');
            }
        });
    }

    $('#search-box').on('input', updateBooks);
    $('#search-type').on('change', function () {
        const searchType = $(this).val();
        const placeholders = {
            'title': 'Введите название...',
            'author': 'Введите автора...',
            'year': 'Введите год...',
            'isbn': 'Введите ISBN...'
        };
        $('#search-box').attr('placeholder', placeholders[searchType] || 'Введите запрос...');
    });

    $('#search-form').on('submit', function (e) {
        e.preventDefault();
        updateBooks();
    });

    $('#openModal').on('click', () => $('#modal').css('display', 'flex'));
    $('#closeModal').on('click', () => $('#modal').hide());
    $('#closeModalInventory').on('click', () => $('#modalInventory').hide());
    $('#closeModalWriteOff').on('click', () => $('#modalWriteOff').hide());

    window.onclick = (e) => {
        if (e.target === document.getElementById('modal')) $('#modal').hide();
        if (e.target === document.getElementById('modalInventory')) $('#modalInventory').hide();
        if (e.target === document.getElementById('modalWriteOff')) $('#modalWriteOff').hide();
    };

    $('input[name="title"]').on('blur', function () {
        const title = $(this).val().trim();
        if (!title) return;

        console.log('Запрос обложек для:', title);
        $.get('/books/fetch-cover/', { title: title }, function (data) {
            console.log('Ответ от /books/fetch-cover/:', data);

            if (data.image_urls && data.image_urls.length > 0) {
                let previewHTML = '<div class="cover-scroll">';
                data.image_urls.forEach(url => {
                    previewHTML += `<img src="${url}" class="cover-option" style="margin: 5px; width: 80px;">`;
                });
                previewHTML += '</div>';
                $('#cover-preview').html(previewHTML);

                $('.cover-option').on('click', function () {
                    $('.cover-option').removeClass('selected');
                    $(this).addClass('selected');
                    const selectedUrl = $(this).attr('src');
                    $('input[name="cover_auto"]').val(selectedUrl);
                    console.log('Выбрана обложка:', selectedUrl);
                });
            } else {
                console.log('Обложки не найдены:', data);
            }

            if (data.authors && data.authors.length > 0) {
                let authorsHTML = '<div style="background:#f2f2f2; border:1px solid #ccc; padding: 5px;">';
                data.authors.forEach(author => {
                    authorsHTML += `<div class="author-option" style="cursor:pointer; padding:4px 6px;">${author}</div>`;
                });
                authorsHTML += '</div>';
                $('#author-suggestions').html(authorsHTML);

                $('.author-option').on('click', function () {
                    $('#author-input').val($(this).text());
                    $('#author-suggestions').empty();
                });
            }
        }).fail(function (xhr) {
            console.error('Ошибка при загрузке обложек:', xhr.responseText);
        });
    });

    $('#add-book-form').on('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const $button = $(this).find('button[type="submit"]');

        for (let [key, value] of formData.entries()) {
            console.log(`FormData: ${key} = ${value}`);
        }

        $button.prop('disabled', true).text('Сохранение...');

        $.ajax({
            url: "/books/add/",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                if (data.success) {
                    console.log('Книга успешно добавлена');
                    $('#modal').hide();
                    $('#add-book-form')[0].reset();
                    $('#cover-preview').empty();
                    $('#form-errors').empty();
                    updateBooks();
                }
            },
            error: function (xhr) {
                console.error('Ошибка при добавлении книги:', xhr.responseJSON);
                const errors = xhr.responseJSON?.errors;
                if (errors) {
                    let html = '';
                    for (const field in errors) {
                        html += `<p>${field}: ${errors[field].join(', ')}</p>`;
                    }
                    $('#form-errors').html(html);
                } else {
                    $('#form-errors').html('<p>Произошла ошибка при добавлении книги. Попробуйте позже.</p>');
                }
            },
            complete: function () {
                setTimeout(function () {
                    $button.prop('disabled', false).text('Сохранить');
                }, 2000);
            }
        });
    });

    $('#openWriteOffModal').on('click', () => $('#modalWriteOff').css('display', 'flex'));
    $('#writeOffForm').on('submit', function (e) {
        e.preventDefault();
        const inventoryNumber = $('#inventoryNumber').val().trim();
        const reason = $('#writeOffReason').val().trim();
        const $button = $('#confirmWriteOff'); // Кнопка "Списать"
        const $errors = $('#write-off-errors');

        if (!inventoryNumber) {
            $errors.text('Ошибка: Введите инвентарный номер.');
            return;
        }

        $button.prop('disabled', true).text('Обработка...');
        $errors.empty();

        $.post({
            url: '/books/write-off-by-inventory/',
            data: {
                inventory_number: inventoryNumber,
                reason: reason,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                if (data.success) {
                    alert(data.message); // Уведомление об успехе
                    updateBooks();
                    $('#writeOffForm')[0].reset(); // Сбрасываем форму
                    $('#modalWriteOff').hide(); // Закрываем окно
                } else {
                    $errors.text('Ошибка: ' + (data.message || 'Неверный инвентарный номер.'));
                }
            },
            error: function (xhr) {
                console.error('Ошибка при списании:', xhr.responseText);
                $errors.text('Произошла ошибка при списании. Проверьте соединение.');
            },
            complete: function () {
                $button.prop('disabled', false).text('Списать'); // Восстанавливаем текст кнопки
            }
        });
    });

    $('#confirmAndPrintWriteOff').on('click', function () {
        const inventoryNumber = $('#inventoryNumber').val().trim();
        const reason = $('#writeOffReason').val().trim();
        const $button = $(this); // Кнопка "Списать и печатать"
        const $errors = $('#write-off-errors');

        if (!inventoryNumber) {
            $errors.text('Ошибка: Введите инвентарный номер.');
            return;
        }

        $button.prop('disabled', true).text('Обработка...');
        $errors.empty();

        $.post({
            url: '/books/write-off-by-inventory/',
            data: {
                inventory_number: inventoryNumber,
                reason: reason,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                if (data.success) {
                    alert(data.message); // Уведомление об успехе
                    updateBooks();
                    const printHtml = data.print_html;
                    const win = window.open('', '_blank');
                    win.document.write(printHtml);
                    win.document.close();
                    win.print();
                    win.close();
                    $('#writeOffForm')[0].reset(); // Сбрасываем форму
                    $('#modalWriteOff').hide(); // Закрываем окно
                } else {
                    $errors.text('Ошибка: ' + (data.message || 'Неверный инвентарный номер.'));
                }
            },
            error: function (xhr) {
                console.error('Ошибка при списании:', xhr.responseText);
                $errors.text('Произошла ошибка при списании. Проверьте соединение.');
            },
            complete: function () {
                $button.prop('disabled', false).text('Списать и распечатать акт'); // Восстанавливаем текст кнопки
            }
        });
    });

    bindCardClickEvents(); // Инициализация при загрузке страницы
});