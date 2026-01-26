import React, { useRef } from "react";
import { useNavigate } from 'react-router-dom';

export default () => {
    const navigate = useNavigate();
    const footerRef = useRef<HTMLDivElement>(null);

    const scrollToFooter = () => {
        footerRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // Ajuste: font-medium para el menú
    const textMenuClass = "text-[#0D0D1B] text-sm transition-colors duration-300 hover:text-[#1213ed] active:text-[#1213ed] cursor-pointer font-medium";
    const buttonPressEffect = "transition-transform duration-100 active:scale-95";

    return (
        <div className="flex flex-col bg-white w-full">
            
            {/* --- NAVBAR --- */}
            <div className="flex justify-between items-center bg-[#FFFFFFCC] py-4 px-10 sticky top-0 z-50 backdrop-blur-sm">
                <img
                    src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/549wbqn9_expires_30_days.png"}
                    className="w-[148px] h-[42px] object-contain"
                    alt="Logo"
                />
                <div className="flex-1 flex justify-center items-center gap-12">
                    <span onClick={() => navigate("/carreras")} className={textMenuClass}>{"Carreras"}</span>
                    <span onClick={() => navigate("/universidades")} className={textMenuClass}>{"Universidades"}</span>
                    <span onClick={scrollToFooter} className={textMenuClass}>{"Nosotros"}</span>
                </div>
                <button 
                    className={`flex items-center gap-2 bg-[#1313EC] py-2.5 px-6 rounded-full border-0 ${buttonPressEffect}`}
                    style={{ boxShadow: "0px 4px 6px #1313EC33" }}
                    onClick={() => alert("Login presionado")}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    {/* Botón: font-bold */}
                    <span className="text-white text-sm font-bold">{"Iniciar Sesión"}</span>
                </button>
            </div>

            {/* --- HERO SECTION --- */}
            <div className="flex flex-col items-center py-[156px]" style={{ background: "linear-gradient(180deg, #AAD5FF, #E7E7F3)" }}>
                {/* Título Principal: font-black */}
                <span className="text-[#0D0D1B] text-7xl font-black text-center w-full max-w-[1029px] mb-[17px] leading-tight">
                    {"Encuentra la Universidad de \ntus sueños"}
                </span>
                <div className="mb-8">
                    {/* Texto normal */}
                    <span className="text-[#4C4C9A] text-xl font-normal">
                        {"El mejor consejero para elegir tu universidad con IA"}
                    </span>
                </div>
                <button className={`flex items-center bg-[#1313EC] py-5 px-10 gap-2 rounded-full border-0 ${buttonPressEffect}`}
                    style={{ boxShadow: "0px 25px 50px #1313EC66" }}
                    onClick={() => navigate("/asistente")}>
                    <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/phwmyikc_expires_30_days.png"} className="w-6 h-[27px] rounded-full object-contain" />
                    {/* Botón: font-bold */}
                    <span className="text-white text-lg font-bold">{"Empieza YA"}</span>
                </button>
            </div>

            {/* --- IMÁGENES FLOTANTES --- */}
            <div className="flex items-center justify-center bg-white relative py-[74px] my-10 overflow-hidden">
                <div className="flex items-center gap-6 relative z-10">
                    <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/2pybayz3_expires_30_days.png" className="w-[100px] h-[100px] object-contain" />
                    <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/qt275mx7_expires_30_days.png" className="w-[180px] h-[190px] object-contain" />
                    <div className="relative">
                        <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/emnatuwr_expires_30_days.png" className="w-[390px] h-[190px] object-contain" />
                        <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/bep45rw3_expires_30_days.png" className="w-[130px] h-[130px] absolute -bottom-10 -right-14 object-contain" />
                        <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/z71hgmj6_expires_30_days.png" className="w-[140px] h-[120px] absolute -bottom-10 -left-16 object-contain" />
                    </div>
                    <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/kawkjqbw_expires_30_days.png" className="w-[200px] h-[200px] object-contain" />
                    <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/q4rvkicj_expires_30_days.png" className="w-[100px] h-[100px] object-contain" />
                </div>
                <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/twkzpv6c_expires_30_days.png" className="w-[168px] h-28 absolute top-10 left-[20%] object-contain opacity-50" />
                <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/41ghxufy_expires_30_days.png" className="w-28 h-28 absolute top-10 right-[20%] object-contain opacity-50" />
            </div>

            {/* --- SECCIÓN ¿POR QUÉ ELEGIRNOS? --- */}
            <div className="flex flex-col bg-[#F6F6F8] py-20 px-[210px] gap-16">
                <div className="flex flex-col gap-4 text-center">
                    {/* Título Principal: font-black */}
                    <span className="text-[#0D0D1B] text-4xl font-black">{"¿Por qué elegir UniDream?"}</span>
                    <span className="text-[#4C4C9A] text-base mx-auto max-w-[706px] whitespace-pre-line font-normal">
                        {"Cientos de ecuatorianos al momento de graduarse se encuentran con uno de los dilemas más espantosos para un joven cruzando la pubertad; ¿Qué haré con mi vida?.\n\nEntonces los aventurados en continuar con sus estudios prefieren seguir el camino de la universidad, pero se vuelven a chocar con la pared; ¿Qué carrera puedo seguir y en dónde?\nAquí es donde UniDream se vuelve tu mejor amigo:"}
                    </span>
                </div>

                <div className="flex flex-col gap-8">
                    {/* Tarjeta 1 */}
                    <div className="flex justify-start">
                        <div className="flex items-center bg-white p-8 gap-6 rounded-full border border-[#E7E7F3] shadow-sm max-w-4xl">
                            <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/94hdy3q5_expires_30_days.png" className="w-16 h-16 rounded-full" />
                            <div>
                                {/* Subtítulo: font-bold */}
                                <h3 className="text-[#0D0D1B] text-xl font-bold">Recomendaciones IA</h3>
                                <p className="text-[#4C4C9A] text-base font-normal">Trabaja con un sistema avanzado de IA con el cuál entenderá todos tus gustos, pasatiempos y aspiraciones.</p>
                            </div>
                        </div>
                    </div>
                    {/* Tarjeta 2 */}
                    <div className="flex justify-end">
                        <div className="flex items-center bg-white p-8 gap-6 rounded-full border border-[#E7E7F3] shadow-sm max-w-4xl">
                            <div className="text-right">
                                <h3 className="text-[#0D0D1B] text-xl font-bold">Datos Verificados</h3>
                                <p className="text-[#4C4C9A] text-base font-normal">Su base de datos reúne a todas las universidades registradas por la Senescyt en el Ecuador.</p>
                            </div>
                            <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/uz0mfrq6_expires_30_days.png" className="w-16 h-16 rounded-full" />
                        </div>
                    </div>
                    {/* Tarjeta 3 */}
                    <div className="flex justify-start">
                        <div className="flex items-center bg-white p-8 gap-6 rounded-full border border-[#E7E7F3] shadow-sm max-w-4xl">
                            <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/x0r37i6l_expires_30_days.png" className="w-16 h-16 rounded-full" />
                            <div>
                                <h3 className="text-[#0D0D1B] text-xl font-bold">Conexión Directa</h3>
                                <p className="text-[#4C4C9A] text-base font-normal">UniDream reúne a cada una de estas instituciones y se garantiza que la información siempre estará actualizada.</p>
                            </div>
                        </div>
                    </div>
                    {/* Tarjeta 4 */}
                    <div className="flex justify-end">
                        <div className="flex items-center bg-white p-8 gap-6 rounded-full border border-[#E7E7F3] shadow-sm max-w-4xl">
                            <div className="text-right">
                                <h3 className="text-[#0D0D1B] text-xl font-bold">Plan de Carrera</h3>
                                <p className="text-[#4C4C9A] text-base font-normal">Visualiza tu futuro profesional y las oportunidades laborales de cada carrera.</p>
                            </div>
                            <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/742xpcny_expires_30_days.png" className="w-16 h-16 rounded-full" />
                        </div>
                    </div>
                </div>
            </div>

            {/* --- CÓMO FUNCIONA --- */}
            <div className="flex flex-col bg-white py-24 px-[210px] gap-16">
                <div className="text-center gap-4 flex flex-col">
                    <span className="text-[#0D0D1B] text-4xl font-black">{"¿Cómo funciona?"}</span>
                    <span className="text-[#4C4C9A] text-base font-normal">{'Cuatro pasos simples para transformar tu futuro académico.'}</span>
                </div>

                <div className="flex justify-between items-start gap-4">
                    <div className="flex flex-1 flex-col items-center gap-4">
                        <div className="flex justify-center items-center bg-[#1313EC] w-20 h-20 rounded-full shadow-lg">
                            <span className="text-white text-2xl font-bold">1</span>
                        </div>
                        <span className="text-[#0D0D1B] text-lg font-bold">{"Empieza ya"}</span>
                        <span className="text-[#4C4C9A] text-sm text-center font-normal">{"Un click en Empieza ya te llevará a encontrar la universidad de tus sueños"}</span>
                    </div>
                    <div className="flex flex-1 flex-col items-center gap-4">
                        <div className="flex justify-center items-center bg-[#1313EC33] w-20 h-20 rounded-full">
                            <span className="text-[#1313EC] text-2xl font-bold">2</span>
                        </div>
                        <span className="text-[#0D0D1B] text-lg font-bold">{"Responde el test IA"}</span>
                        <span className="text-[#4C4C9A] text-sm text-center font-normal">{"Cuéntanos cuáles son tus habilidades, gustos, y qué buscas en tu futuro."}</span>
                    </div>
                    <div className="flex flex-1 flex-col items-center gap-4">
                        <div className="flex justify-center items-center bg-[#1313EC33] w-20 h-20 rounded-full">
                            <span className="text-[#1313EC] text-2xl font-bold">3</span>
                        </div>
                        <span className="text-[#0D0D1B] text-lg font-bold">{"Compara opciones"}</span>
                        <span className="text-[#4C4C9A] text-sm text-center font-normal">{"Analiza mallas, costos y beneficios de las mejores universidades."}</span>
                    </div>
                    <div className="flex flex-1 flex-col items-center gap-4">
                        <div className="flex justify-center items-center bg-[#1313EC33] w-20 h-20 rounded-full">
                            <span className="text-[#1313EC] text-2xl font-bold">4</span>
                        </div>
                        <span className="text-[#0D0D1B] text-lg font-bold">{"Postula"}</span>
                        <span className="text-[#4C4C9A] text-sm text-center font-normal">{"Si quieres saber más información puedes ver las listas de Universidades y carreras."}</span>
                    </div>
                </div>
            </div>

            {/* --- FOOTER --- */}
            <div ref={footerRef} className="bg-[#0A0A14] py-16 px-20">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-20 text-white">
                    <div className="col-span-1 flex flex-col gap-6">
                        <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/w9hmg2ml_expires_30_days.png"} className="w-48 object-contain" alt="UniDream Logo"/>
                        <p className="text-gray-400 text-sm leading-relaxed font-normal">
                            {"Somos un equipo apasionado de estudiantes y desarrolladores comprometidos con democratizar el acceso a la orientación profesional de calidad mediante el uso responsable de la Inteligencia Artificial."}
                        </p>
                    </div>
                    <div className="col-span-1 flex flex-col gap-4">
                        {/* Subtítulos Footer: font-bold */}
                        <h4 className="text-lg font-bold mb-2">Plataforma</h4>
                        <span className="text-gray-400 text-sm hover:text-white cursor-pointer font-normal">Directorio de Carreras</span>
                        <span className="text-gray-400 text-sm hover:text-white cursor-pointer font-normal">Ranking de Universidades</span>
                        <span className="text-gray-400 text-sm hover:text-white cursor-pointer font-normal">Datos 100% enfocados en el país</span>
                        <span className="text-gray-400 text-sm hover:text-white cursor-pointer font-normal">Test Vocacional IA</span>
                    </div>
                    <div className="col-span-1 flex flex-col gap-4"></div>
                    <div className="col-span-1 flex flex-col gap-4">
                        <h4 className="text-lg font-bold mb-2">Suscríbete</h4>
                        <p className="text-gray-400 text-sm mb-4 font-normal">Recibe las últimas noticias sobre admisiones y nuevas carreras.</p>
                        <div className="flex flex-col gap-3">
                            <input type="email" placeholder="Tu correo electrónico" className="bg-[#FFFFFF1A] text-white p-3 rounded-full border border-[#FFFFFF33] outline-none focus:border-blue-500 transition-colors font-normal"/>
                            <button className={`bg-[#1313EC] text-white py-3 rounded-full font-bold hover:bg-[#0f0fb5] transition-colors ${buttonPressEffect}`} onClick={() => alert("Suscrito!")}>
                                Suscribirme
                            </button>
                        </div>
                    </div>
                </div>
                <div className="border-t border-gray-800 pt-8 text-center">
                    <span className="text-gray-500 text-sm font-normal">{"© 2026 UniDream Platform. Todos los derechos reservados. Diseñado para el éxito estudiantil."}</span>
                </div>
            </div>
        </div>
    )
}