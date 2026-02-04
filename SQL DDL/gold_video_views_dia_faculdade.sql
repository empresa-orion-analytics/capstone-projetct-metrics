CREATE TABLE public.gold_video_views_dia_faculdade (
	data_postagem date NULL,
	faculdade varchar(100) NULL,
	total_views int8 NULL,
	total_likes int4 NULL,
	total_comentarios int4 NULL,
	total_videos int4 NULL,
	CONSTRAINT unique_dia_faculdade UNIQUE (data_postagem, faculdade)
);