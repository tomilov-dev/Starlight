export interface Country {
  id: number;

  iso: string;
  name_en: string;
  name_ru: string | null;
  image_url: string | null;
}
