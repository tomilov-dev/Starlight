import { MovieType } from './movie.model';

export interface IMDbMovieBase {
  id: number;
  imdb_mvid: string;

  name_en: string;
  name_ru: string | null;
  slug: string;

  is_adult: boolean;
  runtime: number | null;

  rate: number | null;
  wrate: number | null;
  votes: number | null;

  start_year: number;
  end_year: number | null;
  image_url: string | null;

  imdb_extra_added: boolean;
  tmdb_added: boolean;
  principals_added: boolean;

  type: MovieType;
}
