$(function () {
    function updateBooks() {
        const searchType = $('#search-type').val();
        const searchTerm = $('#search-box').val();

        $.get("/books/ajax-book-list/", {
            type: searchType,
            q: searchTerm
        }, function (data) {
            $('.book-container').html(data.html);
            bindCardClickEvents();
        }).fail(function (xhr) {
            console.error('Ошибка при загрузке книг:', xhr.responseText);
        });
    }
    $(function () {
    // Real-time calculation of price_one
    function updatePriceOne() {
        const acquisitionPrice = parseFloat($('input[name="acquisition_price"]').val()) || 0;
        const quantity = parseInt($('input[name="quantity"]').val()) || 0;
        const priceOne = quantity > 0 ? (acquisitionPrice / quantity).toFixed(2) : '';
        $('input[name="price_one"]').val(priceOne);
    }

    $('input[name="acquisition_price"], input[name="quantity"]').on('input', updatePriceOne);
    });
    function bindCardClickEvents() {
        $('.book-card').off('click').on('click', function (e) {
            if ($(e.target).hasClass('delete-icon') || $(e.target).closest('.delete-icon').length) {
                return;
            }
            const bookId = $(this).data('book-id');
            const quantity = parseInt($(this).find('p:contains("Количество экземпляров:")').text().replace('Количество экземпляров:', '').trim());
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
            const quantity = parseInt(bookCard.find('p:contains("Количество экземпляров:")').text().replace('Количество экземпляров:', '').trim());
            if (quantity > 1) {
                const inventoryList = bookCard.data('inventory').split(',').map(item => `<li>${item.trim()}</li>`).join('');
                $('#inventory-book-title').text(bookCard.find('strong').text());
                $('#inventory-items').html(inventoryList);
                $('#modalInventory').css('display', 'flex');
            }
        });
    }

    // Загрузка номеров партий в select
    function loadBatchNumbers($select) {
        $.get('/books/suggest-batch/', { query: '' }, function (data) {
            if (data.suggestions && data.suggestions.length) {
                $select.empty().append('<option value="">Выберите № партии</option>');
                data.suggestions.forEach(batch => {
                    $select.append(`<option value="${batch}">${batch}</option>`);
                });
            } else {
                $select.empty().append('<option value="">Нет доступных партий</option>');
            }
        }).fail(function (xhr) {
            console.error('Ошибка при загрузке номеров партий:', xhr.responseText);
            $select.empty().append('<option value="">Ошибка загрузки партий</option>');
        });
    }

    // Автозаполнение полей при выборе номера партии
    // Автозаполнение полей при выборе номера партии
    $(document).on('change', '.batch-input', function () {
        const $select = $(this);
        const batchNumber = $select.val();
        const $bookEntry = $select.closest('.book-entry');

        if (!batchNumber) {
            $bookEntry.find('input[name="title[]"]').val('');
            $bookEntry.find('input[name="author[]"]').val('');
            $bookEntry.find('input[name="year[]"]').val('');
            $bookEntry.find('input[name="publisher[]"]').val('');
            $bookEntry.find('input[name="inventory_digit[]"]').val('');
            $bookEntry.find('input[name="quantity[]"]').val('');
            $bookEntry.find('input[name="unit_price[]"]').val('');
            return;
        }

        console.log('Отправка запроса для batch_number:', batchNumber);

        $.get('/books/book-details-by-batch/', { batch_number: batchNumber }, function (data) {
            if (!data.error) {
                console.log('Получены данные:', data);
                $bookEntry.find('input[name="title[]"]').val(data.title || '');
                $bookEntry.find('input[name="author[]"]').val(data.author || '');
                $bookEntry.find('input[name="year[]"]').val(data.year || '');
                $bookEntry.find('input[name="publisher[]"]').val(data.publisher || '');
                $bookEntry.find('input[name="inventory_digit[]"]').val(data.inventory_digit || '');
                $bookEntry.find('input[name="quantity[]"]').val(data.quantity || 1);
                $bookEntry.find('input[name="unit_price[]"]').val(data.unit_price || '');
            } else {
                console.error('Ошибка от сервера:', data.error);
                alert('Ошибка: ' + data.error);
                $select.val('');
            }
        }).fail(function (xhr) {
            console.error('Ошибка AJAX-запроса:', {
                status: xhr.status,
                statusText: xhr.statusText,
                responseText: xhr.responseText
            });
            alert('Ошибка при загрузке данных книги: ' + (xhr.responseJSON?.error || 'Проверьте соединение или данные.'));
            $select.val('');
        });
    });

    // Добавление новой книги в форму списания
        $('#addAnotherBook').on('click', function () {
            console.log('Добавление новой книги'); // Отладка
            const bookCount = $('#books-to-write-off .book-entry').length + 1;
            const newEntry = `
                <h3>Книга ${bookCount}</h3>
                <div class="book-entry">
                    <p>
                        <select name="batch_number[]" class="batch-input" required style="width: 100%; height: 40px; font-size: 16px;">
                            <option value="">Выберите № партии</option>
                        </select>
                        <div class="batch-suggestions" style="margin-top: 5px;"></div>
                    </p>
                    <p><input type="text" name="inventory_digit[]" placeholder="Инвентарный номер (например, 22, 44)" required style="width: 100%; height: 40px;"></p>
                    <p><input type="number" name="quantity[]" placeholder="Количество экземпляров" min="1" required style="width: 100%; height: 40px;"></p>
                    <p><input type="text" name="title[]" class="title-input" placeholder="Название учебника (например, Математика 9 класс)" required style="width: 100%; height: 40px; font-size: 16px;"></p>
                    <p><input type="text" name="author[]" placeholder="Автор" required style="width: 100%; height: 40px;"></p>
                    <p><input type="number" name="year[]" placeholder="Год выпуска" required style="width: 100%; height: 40px;"></p>
                    <p><input type="text" name="publisher[]" placeholder="Издательство" required style="width: 100%; height: 40px;"></p>
                    <p><input type="number" name="unit_price[]" placeholder="Цена за экземпляр (руб.)" step="0.01" required style="width: 100%; height: 40px;"></p>
                    <button type="button" class="remove-book-entry add-button" style="margin-top: 10px;">Удалить книгу</button>
                </div>
            `;
            $('#books-to-write-off').append(newEntry);
            loadBatchNumbers($('.book-entry:last .batch-input'));
        });

        // Удаление книги из формы
        $(document).on('click', '.remove-book-entry', function () {
            $(this).closest('.book-entry').prev('h3').remove();
            $(this).closest('.book-entry').remove();
            $('#books-to-write-off h3').each(function (index) {
                $(this).text(`Книга ${index + 1}`);
            });
        });



    // Валидация формы перед отправкой
    function validateForm() {
        let isValid = true;
        console.log('Валидация формы:'); // Отладка

        // Проверка единого поля reason
        const reason = $('#reason').val();
        console.log('Причина списания:', reason); // Отладка
        if (!reason || !reason.trim()) {
            isValid = false;
            $('#write-off-errors').text('Ошибка: Укажите причину списания.');
            return false;
        }

        $('.book-entry').each(function (index) {
            const $entry = $(this);
            console.log(`Проверка книги ${index + 1}`); // Отладка
            if (!$entry.find('select[name="batch_number[]"]').val()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Выберите номер партии для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="inventory_digit[]"]').val().trim()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Заполните инвентарный номер для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="quantity[]"]').val() || parseInt($entry.find('input[name="quantity[]"]').val()) < 1) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Укажите корректное количество экземпляров для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="title[]"]').val().trim()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Заполните название учебника для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="author[]"]').val().trim()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Заполните автора для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="year[]"]').val()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Укажите год выпуска для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="publisher[]"]').val().trim()) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Заполните издательство для всех книг.');
                return false;
            }
            if (!$entry.find('input[name="unit_price[]"]').val() || parseFloat($entry.find('input[name="unit_price[]"]').val()) <= 0) {
                isValid = false;
                $('#write-off-errors').text('Ошибка: Укажите корректную цену за экземпляр для всех книг.');
                return false;
            }
        });
        return isValid;
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
        if (e.target === document.getElementById('modal')) $('#modal').hide();        if (e.target === document.getElementById('modalInventory')) $('#modalInventory').hide();

        if (e.target === document.getElementById('modalWriteOff')) $('#modalWriteOff').hide();
    };

    $('input[name="title"]').on('blur', function () {
        const title = $(this).val().trim();
        if (!title) return;

        $.get('/books/fetch-cover/', { title: title }, function (data) {
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
                    $('input[name="cover_auto"]').val($(this).attr('src'));
                });
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


    // Открытие модального окна списания
    $('#openWriteOffModal').on('click', () => {
        $('#modalWriteOff').css('display', 'flex');
        loadBatchNumbers($('.batch-input')); // Загружаем номера партий
    });




    // Списание и печать акта
    $('#confirmAndPrintWriteOff').off('click').on('click', function () {
        const $button = $(this);
        const $errors = $('#write-off-errors');
        const formData = new FormData($('#writeOffForm')[0]);

        if (!validateForm()) {
            $button.prop('disabled', false).text('Списать и распечатать акт');
            return;
        }

        console.log('Отправляемые данные формы для печати:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }

        $button.prop('disabled', true).text('Обработка...');
        $errors.empty();

        $.ajax({
            url: '/books/write-off-books/',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                console.log('Ответ сервера:', data);
                if (data.success) {
                    alert(data.message);
                    updateBooks();
                    const printHtml = data.print_html;
                    if (printHtml) {
                        const win = window.open('', '_blank');
                        if (win) {
                            win.document.write(printHtml);
                            win.document.close();
                            win.focus();
                            setTimeout(() => {
                                win.print();
                                win.close();
                            }, 500);
                        } else {
                            alert('Не удалось открыть окно печати. Проверьте настройки браузера.');
                        }
                    } else {
                        alert('Ошибка: HTML для печати не получен.');
                    }
                    $('#writeOffForm')[0].reset();
                    console.log('Сброс формы: установка одной книги'); // Отладка
                    $('#books-to-write-off').html(`
                        <h3>Книга 1</h3>
                        <div class="book-entry">
                            <p>
                                <select name="batch_number[]" class="batch-input" required style="width: 100%; height: 40px; font-size: 16px;">
                                    <option value="">Выберите № партии</option>
                                </select>
                                <div class="batch-suggestions" style="margin-top: 5px;"></div>
                            </p>
                            <p><input type="text" name="inventory_digit[]" placeholder="Инвентарный номер (например, 22, 44)" required style="width: 100%; height: 40px;"></p>
                            <p><input type="number" name="quantity[]" placeholder="Количество экземпляров" min="1" required style="width: 100%; height: 40px;"></p>
                            <p><input type="text" name="author[]" placeholder="Автор" required style="width: 100%; height: 40px;"></p>
                            <p><input type="number" name="year[]" placeholder="Год выпуска" required style="width: 100%; height: 40px;"></p>
                           
                            <p><input type="text" name="publisher[]" placeholder="Издательство" required style="width: 100%; height: 40px;"></p>
                            <p><input type="number" name="unit_price[]" placeholder="Цена за экземпляр (руб.)" step="0.01" required style="width: 100%; height: 40px;"></p>
                        </div>
                    `);
                    loadBatchNumbers($('.batch-input')); // Перезагружаем номера партий
                    $('#modalWriteOff').hide();
                } else {
                    console.error('Ошибка от сервера:', data.message);
                    $errors.text('Ошибка: ' + (data.message || 'Ошибка при списании книг.'));
                }
            },
            error: function (xhr) {
                console.error('Ошибка при списании:', {
                    status: xhr.status,
                    responseText: xhr.responseText,
                    responseJSON: xhr.responseJSON
                });
                $errors.text('Ошибка: ' + (xhr.responseJSON?.message || 'Произошла ошибка при списании. Проверьте данные.'));
            },
            complete: function () {
                $button.prop('disabled', false).text('Списать и распечатать акт');
            }
        });
    });
    bindCardClickEvents();
});