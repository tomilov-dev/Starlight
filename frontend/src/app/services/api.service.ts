import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Genre, GenreMovies } from '../models/genre.model';
import { Movie } from '../models/movie.model';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getGenres(): Observable<Genre[]> {
    return this.http.get<Genre[]>(`${this.baseUrl}/genres`);
  }

  getMovie(slug: string): Observable<Movie> {
    return this.http.get<Movie>(`${this.baseUrl}/movies/${slug}`);
  }

  getGenreMovies(slug: string): Observable<GenreMovies> {
    return this.http.get<GenreMovies>(`${this.baseUrl}/genres/${slug}`);
  }
}
