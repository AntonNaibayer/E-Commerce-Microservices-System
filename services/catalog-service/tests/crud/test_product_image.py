import uuid

from app.db.crud import product_image as product_image_crud


async def test_create_product_image(
    db_session,
    product,
):
    product_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/image.jpg",
        sort_order=1,
    )

    assert product_image.id is not None
    assert product_image.product_id == product.id
    assert product_image.url == "https://example.com/image.jpg"
    assert product_image.alt_text is None
    assert product_image.sort_order == 1

async def test_create_product_image_with_alt_text(
    db_session,
    product,
):
    product_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/iphone.jpg",
        sort_order=1,
        alt_text="iPhone 17",
    )

    assert product_image.product_id == product.id
    assert product_image.alt_text == "iPhone 17"

async def test_get_product_image_by_id(
    db_session,
    product,
):
    product_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/image.jpg",
        sort_order=1,
    )

    found_image = await product_image_crud.get_product_image_by_id(
        session=db_session,
        product_image_id=product_image.id,
    )

    assert found_image is not None
    assert found_image.id == product_image.id

async def test_get_product_image_by_id_when_not_found(
    db_session,
):
    random_id = uuid.uuid4()

    found_image = await product_image_crud.get_product_image_by_id(
        session=db_session,
        product_image_id=random_id,
    )

    assert found_image is None

async def test_get_product_images(
    db_session,
    product,
):
    first_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/first.jpg",
        sort_order=1,
    )

    second_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/second.jpg",
        sort_order=2,
    )

    third_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/third.jpg",
        sort_order=3,
    )

    images = await product_image_crud.get_product_images(
        session=db_session,
        product_id=product.id,
    )

    assert len(images) == 3
    assert images[0].id == first_image.id
    assert images[1].id == second_image.id
    assert images[2].id == third_image.id

async def test_get_product_images_with_pagination(
    db_session,
    product_factory,
):
    product = await product_factory()

    first_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/first.jpg",
        sort_order=1,
    )

    second_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/second.jpg",
        sort_order=2,
    )

    third_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/third.jpg",
        sort_order=3,
    )

    first_page = await product_image_crud.get_product_images(
        session=db_session,
        product_id=product.id,
        offset=0,
        limit=2,
    )

    assert len(first_page) == 2
    assert first_page[0].id == first_image.id
    assert first_page[1].id == second_image.id

    second_page = await product_image_crud.get_product_images(
        session=db_session,
        product_id=product.id,
        offset=2,
        limit=2,
    )

    assert len(second_page) == 1
    assert second_page[0].id == third_image.id

async def test_update_product_image(
    db_session,
    product_factory,
):
    product = await product_factory()

    product_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/old.jpg",
        sort_order=1,
        alt_text="Old image",
    )

    updated_image = await product_image_crud.update_product_image(
        session=db_session,
        product_image=product_image,
        url="https://example.com/new.jpg",
        sort_order=2,
        alt_text="New image",
    )

    assert updated_image.id == product_image.id
    assert product_image.url == "https://example.com/new.jpg"
    assert product_image.sort_order == 2
    assert product_image.alt_text == "New image"

async def test_delete_product_image(
    db_session,
    product_factory,
):
    product = await product_factory()

    product_image = await product_image_crud.create_product_image(
        session=db_session,
        product_id=product.id,
        url="https://example.com/image.jpg",
        sort_order=1,
    )

    await product_image_crud.delete_product_image(
        session=db_session,
        product_image=product_image,
    )

    found_image = await product_image_crud.get_product_image_by_id(
        session=db_session,
        product_image_id=product_image.id,
    )

    assert found_image is None