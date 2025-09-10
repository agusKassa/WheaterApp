FROM php:8.2-fpm

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    unzip \
    libpq-dev \
    libicu-dev \
    libzip-dev \
    zip \
    && docker-php-ext-install intl pdo pdo_mysql zip opcache \
    && rm -rf /var/lib/apt/lists/*

# Instalar Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Establecer directorio de trabajo
WORKDIR /var/www/html

# Exponer el puerto FPM (no obligatorio, útil si se conecta desde fuera)
EXPOSE 9000

# PHP-FPM ya arranca automáticamente con la imagen base, no hace falta CMD extra
