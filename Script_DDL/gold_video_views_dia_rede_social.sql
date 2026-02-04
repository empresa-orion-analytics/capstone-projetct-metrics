CREATE TABLE public.gold_video_views_dia_rede_social (
	data_postagem date NULL,
	rede_social varchar(50) NULL,
	total_views int8 NULL,
	total_likes int4 NULL,
	total_comentarios int4 NULL,
	total_videos int4 NULL,
	CONSTRAINT unique_dia_rede UNIQUE (data_postagem, rede_social)
);