import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Genre } from '../models/genre.model';
import { IMDbPersonBase, IMDbPersonExtended } from '../models/person.model';
import { IMDbMovieBase } from '../models/base.movie.model';
import { IMDbMovieExtended } from '../models/movie.model';
import { Country } from '../models/country.model';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getGenres(): Observable<Genre[]> {
    return this.http.get<Genre[]>(`${this.baseUrl}/genres`);
  }

  getCountries(): Observable<Country[]> {
    return this.http.get<Country[]>(`${this.baseUrl}/countries`);
  }

  getMovie(slug: string): Observable<IMDbMovieExtended> {
    return this.http.get<IMDbMovieExtended>(`${this.baseUrl}/movies/${slug}`);
  }

  getPerson(slug: string): Observable<IMDbPersonExtended> {
    return this.http.get<IMDbPersonExtended>(`${this.baseUrl}/persons/${slug}`);
  }

  searchMovies(searchQuery: string): Observable<IMDbMovieBase[]> {
    return this.http.get<IMDbMovieBase[]>(
      `${this.baseUrl}/search/movies/${searchQuery}`
    );
  }

  searchPersons(searchQuery: string): Observable<IMDbPersonBase[]> {
    return this.http.get<IMDbPersonBase[]>(
      `${this.baseUrl}/search/persons/${searchQuery}`
    );
  }

  getMoviesByGenre(
    slug: string,
    page: number,
    pageSize: number
  ): Observable<IMDbMovieBase[]> {
    return this.http.get<IMDbMovieBase[]>(`${this.baseUrl}/genres/${slug}`, {
      params: { page: page.toString(), page_size: pageSize.toString() },
    });
  }
}
