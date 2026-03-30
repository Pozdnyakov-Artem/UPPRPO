<template>
    <form class="card" @submit.prevent="submit">
        <h2>Добро пожаловать</h2>
        <div class="form-control">
            <input
                type="email"
                id="email"
                placeholder="Введите email"
                :disabled="isLoading"
                v-model="email">
        </div>

        <div class="form-control">
            <input
                type="password"
                id="password"
                placeholder="Введите пароль"
                :disabled="isLoading"
                v-model="password">
        </div>

        <div class="login-container">
            <button
                class="btn primary"
                type="submit"
                :disabled="!isValid || isLoading"
            >
                Войти
            </button>

            <div class="bottom-actions">
                <button 
                    class="btn"
                    type="button"
                    @click="forgot_password"
                    :disabled="isLoading"
                >
                    Забыл пароль?
                </button>
                <button
                    class="btn"
                    type="button"
                    @click="registration"
                    :disabled="isLoading"
                >
                    Зарегистрироваться
                </button>
            </div>

        </div>

    </form>
</template>

<script>
import axios from 'axios'
export default {
    data() {
        return {
            email: '',
            password: '',
            isLoading: false
        }
    },
    computed: {
        isValid() {
            return this.email !== '' && this.password !== ''
        }
    },
    methods: {
        async submit() {
            if (!this.isValid) {
                console.log('empty_val')
            }   

            this.isLoading = true

            try {
                const response = await axios.post('',{
                    email: this.email,
                    password: this.password
                })

                console.log('Успешная авторизация', response.data);
                
                if (response.data.token) {
                    localStorage.setItem('auth_token', response.data.token);
                }

                // this.$router.push('/dashboard');
                alert('Вы успешно вошли!');

            } catch (error) {
                console.error('Ошибка входа:', error);

                if (error.response) {
                    this.errorMessage = error.response.data.message || 'Неверный email или пароль';
                    
                    if (error.response.status === 401) {
                        this.errorMessage = 'Неверные учетные данные';
                    } else if (error.response.status === 500) {
                        this.errorMessage = 'Ошибка сервера. Попробуйте позже.';
                    }
                } else if (error.request) {
                    this.errorMessage = 'Нет соединения с сервером. Проверьте консоль.';
                } else {
                    this.errorMessage = 'Произошла непредвиденная ошибка';
                }
            } finally {
                this.isLoading = false
            }

        },
        forgot_password () {
            console.log('forgot')
        },
        registration () {

        }
    }
}
</script>
